import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_number(num):
    try:
        return f"{int(num):,}"
    except:
        return str(num)

def get_signal_color(signal):
    if signal == "BUY":
        return "🟢 BUY"
    elif signal == "SELL":
        return "🔴 SELL"
    return "⚪ NONE"

def get_ml_display(ml_result):
    if not ml_result:
        return "N/A", "N/A", "N/A"

    prediction = ml_result.get('prediction', 'N/A')
    probability = ml_result.get('probability', 0)
    recommendation = ml_result.get('recommendation', 'N/A')

    if recommendation == "TAKE TRADE":
        rec_display = f"✅ {recommendation}"
    else:
        rec_display = f"❌ {recommendation}"

    return prediction, f"{probability}%", rec_display

def display_dashboard(stocks, refresh_count=0, performance=None):
    clear_screen()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 130)
    print(f"  🚀 AI/ML STOCK SCREENER | PAPER TRADING DASHBOARD")
    print(f"  📅 {now}  |  🔄 Refresh #{refresh_count}  "
          f"|  📊 Stocks Found: {len(stocks)}")
    print("=" * 130)

    if not stocks:
        print("\n  ⚠️  No stocks match screening criteria.")
        print("  Criteria: LTP ₹30-₹500 | Bid/Ask Qty > minimum")
        print("=" * 130)
        return

    # Main table header
    print(f"\n{'Symbol':<14} {'LTP':>8} {'SMMA20':>8} "
          f"{'SMMA120':>9} {'Signal':<10} "
          f"{'ML Pred':<12} {'Prob':>6} {'Action':<16} "
          f"{'Qty5m':>10} {'Qty20m':>10}")
    print("-" * 130)

    for stock in stocks:
        symbol = stock['symbol']
        ltp = stock['ltp']
        smma20 = stock['smma20']
        smma120 = stock['smma120']
        signal = get_signal_color(stock['signal'])

        ml_result = stock.get('ml_prediction')
        prediction, probability, recommendation = \
            get_ml_display(ml_result)

        qty_5min = format_number(stock['qty_5min'])
        qty_20min = format_number(stock['qty_20min'])

        # Highlight crossover stocks
        prefix = "🔔 " if stock.get('crossover') else "   "

        print(f"{prefix}{symbol:<12} {ltp:>8.2f} {smma20:>8.2f} "
              f"{smma120:>9.2f} {signal:<10} "
              f"{prediction:<12} {probability:>6} "
              f"{recommendation:<16} "
              f"{qty_5min:>10} {qty_20min:>10}")

    print("-" * 130)

    # Market Depth Section
    print(f"\n{'Symbol':<14} {'Bid Price':>10} {'Bid Qty':>12} "
          f"{'Ask Price':>10} {'Ask Qty':>12} "
          f"{'Avg 20m':>10} {'Avg 60m':>10}")
    print("-" * 80)

    for stock in stocks:
        depth = stock.get('depth', {})
        print(f"   {stock['symbol']:<12} "
              f"{depth.get('bid_price', 0):>10.2f} "
              f"{format_number(depth.get('bid_qty', 0)):>12} "
              f"{depth.get('ask_price', 0):>10.2f} "
              f"{format_number(depth.get('ask_qty', 0)):>12} "
              f"{stock['avg_20min']:>10.2f} "
              f"{stock['avg_60min']:>10.2f}")

    print("=" * 130)

    # Crossover Analysis
    crossover_stocks = [s for s in stocks if s.get('crossover')]
    if crossover_stocks:
        print(f"\n  🔔 LIVE CROSSOVER SIGNALS DETECTED!")
        print("-" * 80)
        for stock in crossover_stocks:
            ml = stock.get('ml_prediction')
            if ml:
                print(f"\n  📈 {stock['symbol']} | "
                      f"Signal: {stock['signal']}")
                print(f"     Prediction  : {ml['prediction']}")
                print(f"     Probability : {ml['probability']}%")
                print(f"     Action      : {ml['recommendation']}")
                print(f"     Reason      : {ml['reason']}")

    # Paper Trading Summary
    print(f"\n  📊 PAPER TRADING SUMMARY")
    print("-" * 80)
    if performance:
        print(f"  Total Signals  : {performance.get('total_signals', 0)}")
        print(f"  Accepted       : {performance.get('accepted', 0)}")
        print(f"  Avoided        : {performance.get('avoided', 0)}")
        print(f"  Total Trades   : {performance.get('total_trades', 0)}")
        print(f"  Profitable     : {performance.get('profitable', 0)}")
        print(f"  Unsuccessful   : {performance.get('unprofitable', 0)}")
        print(f"  Success Rate   : {performance.get('success_rate', 0)}%")
        print(f"  Total PnL      : ₹{performance.get('total_pnl', 0)}")
    else:
        print("  Waiting for crossover signals...")

    print("\n  Press Ctrl+C to stop and see final report")
    print("=" * 130)