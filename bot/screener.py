import time
import logging
from datetime import datetime, date
from config import MIN_LTP, MAX_LTP, MIN_BID_QUANTITY, MIN_ASK_QUANTITY
from bot.indicators import (
    calculate_smma,
    detect_crossover,
    calculate_average_price,
    calculate_traded_quantity
)
from bot.ml_model import SignalPredictor
from bot.data_collector import DataCollector
from bot.paper_trader import PaperTrader

logger = logging.getLogger(__name__)

class StockScreener:
    def __init__(self, client):
        self.client = client
        self.predictor = SignalPredictor()
        self.collector = DataCollector()
        self.paper_trader = PaperTrader()
        self.screened_stocks = []
        self.price_history = {}
        self.previous_smma = {}

        # Train on previous day data
        print("📊 Loading previous day data for model training...")
        prev_data = self.collector.load_previous_day_data()
        if prev_data:
            print(f"✅ Found previous day data with {len(prev_data)} symbols!")
            self.predictor.train_on_previous_day(prev_data)
        else:
            print("⚠️ No previous day data found — using synthetic training")
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

        for i, stock in enumerate(all_stocks[:50]):
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

                # Collect real time tick data
                self.collector.add_tick(
                    symbol, ltp, bid_qty, ask_qty)

                # Update price history
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                self.price_history[symbol].append(ltp)

                prices = self.price_history[symbol]

                # Calculate indicators
                smma20 = calculate_smma(prices, 20) or ltp
                smma120 = calculate_smma(prices, 120) or ltp

                # Get LTQ features
                ltq_features = self.collector.get_ltq_features(symbol)

                # Detect crossover
                signal, smma_data = detect_crossover(prices)

                # Check if crossover just happened
                prev_smma = self.previous_smma.get(symbol, {})
                crossover_detected = False

                if prev_smma:
                    prev_20 = prev_smma.get('smma20', smma20)
                    prev_120 = prev_smma.get('smma120', smma120)

                    if prev_20 <= prev_120 and smma20 > smma120:
                        signal = "BUY"
                        crossover_detected = True
                    elif prev_20 >= prev_120 and smma20 < smma120:
                        signal = "SELL"
                        crossover_detected = True

                # Store current SMMA for next comparison
                self.previous_smma[symbol] = {
                    'smma20': smma20,
                    'smma120': smma120
                }

                # Get candle data
                candles = self.client.get_candle_data(
                    token, symbol, interval="ONE_MINUTE")

                # Calculate quantities
                qty_5min = calculate_traded_quantity(candles, 5)
                qty_20min = calculate_traded_quantity(candles, 20)
                qty_60min = calculate_traded_quantity(candles, 60)

                # Calculate average prices
                avg_20min = calculate_average_price(candles, 20)
                avg_60min = calculate_average_price(candles, 60)

                # ML prediction for crossover
                ml_result = None
                if signal and crossover_detected:
                    ml_result = self.predictor.predict_signal(
                        prices, signal, ltq_features)

                    # Paper trading
                    if ml_result['recommendation'] == "TAKE TRADE":
                        self.paper_trader.open_trade(
                            symbol, signal, ltp,
                            ml_result['probability'],
                            ml_result['reason']
                        )
                    else:
                        self.paper_trader.avoided_signals += 1
                        self.paper_trader.total_signals += 1

                # Close paper trade on reverse crossover
                if symbol in self.paper_trader.open_positions:
                    pos = self.paper_trader.open_positions[symbol]
                    if (pos['signal'] == "BUY" and smma20 < smma120) or \
                       (pos['signal'] == "SELL" and smma20 > smma120):
                        self.paper_trader.close_trade(symbol, ltp)

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
                    "crossover": crossover_detected,
                    "qty_5min": qty_5min,
                    "qty_20min": qty_20min,
                    "qty_60min": qty_60min,
                    "avg_20min": avg_20min,
                    "avg_60min": avg_60min,
                    "ml_prediction": ml_result,
                    "depth": depth_data,
                    "ltq_features": ltq_features
                }

                screened.append(stock_data)
                print(f"✅ {symbol} | LTP: {ltp} | "
                      f"Signal: {signal or 'NONE'}")

                time.sleep(0.1)

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

    def get_performance(self):
        """Get paper trading performance"""
        return self.paper_trader.get_performance()

    def display_performance(self):
        """Display performance report"""
        self.paper_trader.display_performance()