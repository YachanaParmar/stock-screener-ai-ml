import time
import logging
from config import MIN_LTP, MAX_LTP, MIN_BID_QUANTITY, MIN_ASK_QUANTITY
from bot.indicators import (
    calculate_smma,
    detect_crossover,
    calculate_average_price,
    calculate_traded_quantity
)
from bot.ml_model import SignalPredictor

logger = logging.getLogger(__name__)

class StockScreener:
    def __init__(self, client):
        self.client = client
        self.predictor = SignalPredictor()
        self.screened_stocks = []
        self.price_history = {}

        # Train ML model on startup
        print("🤖 Training ML model...")
        self.predictor.train_with_synthetic_data()

    def screen_stocks(self):
        """Main screening function"""
        print("\n🔍 Fetching NSE stocks...")
        all_stocks = self.client.get_all_nse_stocks()

        if not all_stocks:
            print("❌ No stocks fetched")
            return []

        print(f"📊 Total NSE stocks: {len(all_stocks)}")
        screened = []

        for i, stock in enumerate(all_stocks[:100]):
            try:
                symbol = stock.get('symbol', '')
                token = stock.get('token', '')

                if not symbol or not token:
                    continue

                # Get LTP
                ltp = self.client.get_ltp(token, symbol)
                if ltp is None:
                    continue

                # Filter by LTP range
                if not (MIN_LTP <= ltp <= MAX_LTP):
                    continue

                # Get market depth
                depth = self.client.get_market_depth(token, symbol)
                if depth is None:
                    continue

                # Extract bid/ask quantities
                bid_qty = depth.get('totBuyQuan', 0)
                ask_qty = depth.get('totSellQuan', 0)

                # Liquidity filter
                if bid_qty < MIN_BID_QUANTITY or ask_qty < MIN_ASK_QUANTITY:
                    continue

                # Get candle data
                candles = self.client.get_candle_data(token, symbol)

                # Update price history
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                self.price_history[symbol].append(ltp)

                prices = self.price_history[symbol]

                # Calculate indicators
                smma20 = calculate_smma(prices, 20) or ltp
                smma120 = calculate_smma(prices, 120) or ltp

                # Detect crossover
                signal, smma_data = detect_crossover(prices)

                # Calculate quantities
                qty_5min = calculate_traded_quantity(candles, 5)
                qty_20min = calculate_traded_quantity(candles, 20)
                qty_60min = calculate_traded_quantity(candles, 60)

                # Calculate average prices
                avg_20min = calculate_average_price(candles, 20)
                avg_60min = calculate_average_price(candles, 60)

                # ML prediction for crossover
                ml_result = None
                if signal:
                    ml_result = self.predictor.predict_signal(
                        prices, signal)

                # Get market depth details
                depth_data = self._extract_depth(depth)

                stock_data = {
                    "symbol": symbol,
                    "ltp": ltp,
                    "bid_qty": bid_qty,
                    "ask_qty": ask_qty,
                    "smma20": round(smma20, 2),
                    "smma120": round(smma120, 2),
                    "signal": signal or "NONE",
                    "qty_5min": qty_5min,
                    "qty_20min": qty_20min,
                    "qty_60min": qty_60min,
                    "avg_20min": avg_20min,
                    "avg_60min": avg_60min,
                    "ml_prediction": ml_result,
                    "depth": depth_data
                }

                screened.append(stock_data)
                print(f"✅ {symbol} | LTP: {ltp} | "
                      f"Signal: {signal or 'NONE'}")

                time.sleep(0.3)  # Rate limiting

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        self.screened_stocks = screened
        return screened

    def _extract_depth(self, depth):
        """Extract market depth information"""
        try:
            buy_orders = depth.get('buyunfulfilled', [{}])
            sell_orders = depth.get('sellunfulfilled', [{}])

            return {
                "bid_price": buy_orders[0].get('price', 0)
                            if buy_orders else 0,
                "bid_qty": buy_orders[0].get('quantity', 0)
                          if buy_orders else 0,
                "ask_price": sell_orders[0].get('price', 0)
                            if sell_orders else 0,
                "ask_qty": sell_orders[0].get('quantity', 0)
                          if sell_orders else 0,
            }
        except Exception:
            return {
                "bid_price": 0,
                "bid_qty": 0,
                "ask_price": 0,
                "ask_qty": 0
            }