import json
import os
import logging
from datetime import datetime, date
import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

class DataCollector:
    def __init__(self):
        self.today = date.today().strftime("%Y-%m-%d")
        self.data_file = f"{DATA_DIR}/market_data_{self.today}.json"
        self.collected_data = {}
        self.load_existing_data()

    def load_existing_data(self):
        """Load existing data if available"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.collected_data = json.load(f)
            logger.info(f"Loaded existing data for {self.today}")

    def save_data(self):
        """Save collected data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.collected_data, f)

    def add_tick(self, symbol, ltp, bid_qty, ask_qty, timestamp=None):
        """Add a price tick for a symbol"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if symbol not in self.collected_data:
            self.collected_data[symbol] = []

        self.collected_data[symbol].append({
            "timestamp": timestamp,
            "ltp": ltp,
            "bid_qty": bid_qty,
            "ask_qty": ask_qty
        })

        # Save every 10 ticks
        if len(self.collected_data[symbol]) % 10 == 0:
            self.save_data()

    def get_symbol_data(self, symbol):
        """Get all collected data for a symbol"""
        return self.collected_data.get(symbol, [])

    def get_previous_day_file(self):
        """Get previous trading day data file"""
        files = sorted([
            f for f in os.listdir(DATA_DIR)
            if f.startswith("market_data_") and f.endswith(".json")
            and f != f"market_data_{self.today}.json"
        ])
        if files:
            return f"{DATA_DIR}/{files[-1]}"
        return None

    def load_previous_day_data(self):
        """Load previous day data for model training"""
        prev_file = self.get_previous_day_file()
        if prev_file and os.path.exists(prev_file):
            with open(prev_file, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded previous day data from {prev_file}")
            return data
        return {}

    def get_ltq_features(self, symbol, window_short=2, window_long=5):
        """Calculate LTQ features for ML model"""
        ticks = self.get_symbol_data(symbol)
        if len(ticks) < window_long:
            return None

        # Calculate average LTP change as proxy for LTQ
        recent_prices = [t['ltp'] for t in ticks[-window_long:]]
        short_prices = recent_prices[-window_short:]
        long_prices = recent_prices

        avg_short = sum(short_prices) / len(short_prices)
        avg_long = sum(long_prices) / len(long_prices)

        price_momentum = (avg_short - avg_long) / avg_long * 100

        bid_quantities = [t['bid_qty'] for t in ticks[-window_long:]]
        ask_quantities = [t['ask_qty'] for t in ticks[-window_long:]]

        avg_bid = sum(bid_quantities) / len(bid_quantities)
        avg_ask = sum(ask_quantities) / len(ask_quantities)

        return {
            "price_momentum": price_momentum,
            "avg_bid_qty": avg_bid,
            "avg_ask_qty": avg_ask,
            "bid_ask_ratio": avg_bid / avg_ask if avg_ask > 0 else 1,
            "short_avg_price": avg_short,
            "long_avg_price": avg_long
        }