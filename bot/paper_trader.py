import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PaperTrader:
    def __init__(self):
        self.trades = []
        self.open_positions = {}
        self.total_signals = 0
        self.accepted_signals = 0
        self.avoided_signals = 0

    def open_trade(self, symbol, signal, ltp, probability, reason):
        """Open a paper trade"""
        self.total_signals += 1

        if probability < 65:
            self.avoided_signals += 1
            logger.info(f"AVOIDED {signal} on {symbol} | Prob: {probability}% | Reason: {reason}")
            return False

        self.accepted_signals += 1
        self.open_positions[symbol] = {
            "symbol": symbol,
            "signal": signal,
            "entry_ltp": ltp,
            "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "probability": probability,
            "reason": reason
        }
        logger.info(f"OPENED {signal} on {symbol} | LTP: {ltp} | Prob: {probability}%")
        return True

    def close_trade(self, symbol, exit_ltp):
        """Close an open paper trade"""
        if symbol not in self.open_positions:
            return None

        position = self.open_positions[symbol]
        entry_ltp = position['entry_ltp']
        signal = position['signal']

        # Calculate PnL
        if signal == "BUY":
            pnl = exit_ltp - entry_ltp
        else:
            pnl = entry_ltp - exit_ltp

        profitable = pnl > 0

        trade = {
            "symbol": symbol,
            "signal": signal,
            "entry_ltp": entry_ltp,
            "exit_ltp": exit_ltp,
            "pnl": round(pnl, 2),
            "profitable": profitable,
            "entry_time": position['entry_time'],
            "exit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "probability": position['probability'],
            "reason": position['reason']
        }

        self.trades.append(trade)
        del self.open_positions[symbol]

        logger.info(f"CLOSED {signal} on {symbol} | Entry: {entry_ltp} | Exit: {exit_ltp} | PnL: {pnl}")
        return trade

    def get_performance(self):
        """Get performance statistics"""
        if not self.trades:
            return {
                "total_signals": self.total_signals,
                "accepted": self.accepted_signals,
                "avoided": self.avoided_signals,
                "total_trades": 0,
                "profitable": 0,
                "unprofitable": 0,
                "success_rate": 0,
                "total_pnl": 0
            }

        profitable = [t for t in self.trades if t['profitable']]
        unprofitable = [t for t in self.trades if not t['profitable']]
        total_pnl = sum(t['pnl'] for t in self.trades)
        success_rate = len(profitable) / len(self.trades) * 100

        return {
            "total_signals": self.total_signals,
            "accepted": self.accepted_signals,
            "avoided": self.avoided_signals,
            "total_trades": len(self.trades),
            "profitable": len(profitable),
            "unprofitable": len(unprofitable),
            "success_rate": round(success_rate, 1),
            "total_pnl": round(total_pnl, 2)
        }

    def display_performance(self):
        """Display performance report"""
        perf = self.get_performance()
        print("\n" + "=" * 60)
        print("  📊 PAPER TRADING PERFORMANCE REPORT")
        print("=" * 60)
        print(f"  Total Signals Generated : {perf['total_signals']}")
        print(f"  Signals Accepted        : {perf['accepted']}")
        print(f"  Signals Avoided         : {perf['avoided']}")
        print(f"  Total Trades Taken      : {perf['total_trades']}")
        print(f"  Profitable Trades       : {perf['profitable']}")
        print(f"  Unsuccessful Trades     : {perf['unprofitable']}")
        print(f"  Success Rate            : {perf['success_rate']}%")
        print(f"  Total Paper PnL         : ₹{perf['total_pnl']}")
        print("=" * 60)

        if self.trades:
            print("\n  📋 TRADE HISTORY")
            print("-" * 60)
            for t in self.trades[-10:]:
                status = "WIN" if t['profitable'] else "❌ LOSS"
                print(f"  {t['symbol']} | {t['signal']} | "
                      f"Entry: {t['entry_ltp']} | "
                      f"Exit: {t['exit_ltp']} | "
                      f"PnL: ₹{t['pnl']} | {status}")
        print("=" * 60)