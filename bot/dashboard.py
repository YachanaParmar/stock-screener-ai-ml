import os
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_number(num):
    """Format large numbers with commas"""
    try:
        return f"{int(num):,}"
    except:
        return str(num)

def get_signal_color(signal):
    """Return signal display text"""
    if signal == "BUY":
        return "🟢 BUY"
    elif signal == "SELL":
        return "🔴 SELL"
    return "⚪ NONE"

def get_ml_display(ml_result):
    """Format ML prediction for display"""
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

def display_dashboard(stocks, refresh_count=0):
    """Display real-time dashboard"""
    clear_screen()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 120)
    print(f"  🚀 STOCK SCREENER & AI/ML ANALYSIS DASHBOARD")
    print(f"  📅 {now}  |  🔄 Refresh #{refresh_count}  "
          f"|  📊 Stocks Found: {len(stocks)}")
    print("=" * 120)
    
    if not stocks:
        print("\n  ⚠️  No stocks match the screening criteria.")
        print("  Criteria: LTP ₹30-₹500 | "
              "Bid Qty > 10L | Ask Qty > 10L")
        print("=" * 120)
        return
    
    # Header
    print(f"\n{'Symbol':<12} {'LTP':>8} {'SMMA20':>8} "
          f"{'SMMA120':>9} {'Signal':<10} "
          f"{'ML Pred':<12} {'Prob':>6} {'Recommend':<16} "
          f"{'Qty5m':>10} {'Qty20m':>10} {'Qty60m':>10}")
    print("-" * 120)
    
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
        qty_60min = format_number(stock['qty_60min'])
        
        print(f"{symbol:<12} {ltp:>8.2f} {smma20:>8.2f} "
              f"{smma120:>9.2f} {signal:<10} "
              f"{prediction:<12} {probability:>6} "
              f"{recommendation:<16} "
              f"{qty_5min:>10} {qty_20min:>10} {qty_60min:>10}")
    
    print("-" * 120)
    
    # Market Depth Section
    print(f"\n{'Symbol':<12} {'Bid Price':>10} {'Bid Qty':>12} "
          f"{'Ask Price':>10} {'Ask Qty':>12} "
          f"{'Avg 20m':>10} {'Avg 60m':>10}")
    print("-" * 80)
    
    for stock in stocks:
        depth = stock.get('depth', {})
        print(f"{stock['symbol']:<12} "
              f"{depth.get('bid_price', 0):>10.2f} "
              f"{format_number(depth.get('bid_qty', 0)):>12} "
              f"{depth.get('ask_price', 0):>10.2f} "
              f"{format_number(depth.get('ask_qty', 0)):>12} "
              f"{stock['avg_20min']:>10.2f} "
              f"{stock['avg_60min']:>10.2f}")
    
    print("=" * 120)
    
    # ML Analysis Details
    crossover_stocks = [s for s in stocks 
                       if s['signal'] != 'NONE']
    
    if crossover_stocks:
        print(f"\n  🤖 AI/ML CROSSOVER ANALYSIS DETAILS")
        print("-" * 80)
        
        for stock in crossover_stocks:
            ml = stock.get('ml_prediction')
            if ml:
                print(f"\n  📈 {stock['symbol']} | "
                      f"Signal: {stock['signal']}")
                print(f"     Prediction : {ml['prediction']}")
                print(f"     Probability: {ml['probability']}%")
                print(f"     Action     : {ml['recommendation']}")
                print(f"     Reason     : {ml['reason']}")
    
    print("\n  Press Ctrl+C to stop the screener")
    print("=" * 120)