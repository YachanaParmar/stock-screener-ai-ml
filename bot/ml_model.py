import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging
import json
import os

logger = logging.getLogger(__name__)

class SignalPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_importance = {}

    def prepare_features(self, prices, signal_type, ltq_features=None):
        """Extract features from price data for ML prediction"""
        if len(prices) < 21:
            return None

        # Price momentum features
        returns_5 = (prices[-1] - prices[-6]) / prices[-6] * 100 if len(prices) >= 6 else 0
        returns_20 = (prices[-1] - prices[-21]) / prices[-21] * 100 if len(prices) >= 21 else 0

        # Volatility
        volatility = np.std(prices[-20:]) if len(prices) >= 20 else 0

        # SMMA values
        smma20 = self._smma(prices, 20)
        smma120 = self._smma(prices, min(120, len(prices)))

        # Distance between SMAs
        smma_distance = ((smma20 - smma120) / smma120) * 100 if smma120 != 0 else 0

        # Price trend
        price_trend = np.polyfit(range(min(20, len(prices))),
                                prices[-min(20, len(prices)):], 1)[0]

        # Signal encoding
        signal_encoded = 1 if signal_type == "BUY" else -1

        features = [
            returns_5,
            returns_20,
            volatility,
            smma20,
            smma120,
            smma_distance,
            price_trend,
            signal_encoded,
            prices[-1],
            np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1],
        ]

        # Add LTQ features if available
        if ltq_features:
            features.extend([
                ltq_features.get('price_momentum', 0),
                ltq_features.get('bid_ask_ratio', 1),
                ltq_features.get('avg_bid_qty', 0),
                ltq_features.get('avg_ask_qty', 0),
            ])
        else:
            features.extend([0, 1, 0, 0])

        return features

    def _smma(self, prices, period):
        """Calculate SMMA"""
        if len(prices) < period:
            return prices[-1]
        first_sma = sum(prices[:period]) / period
        smma = first_sma
        for price in prices[period:]:
            smma = (smma * (period - 1) + price) / period
        return smma

    def train_on_previous_day(self, previous_day_data):
        """Train model on previous day's collected data"""
        if not previous_day_data:
            logger.info("No previous day data — using synthetic training")
            self.train_with_synthetic_data()
            return

        X = []
        y = []

        for symbol, ticks in previous_day_data.items():
            if len(ticks) < 30:
                continue

            prices = [t['ltp'] for t in ticks]

            # Simulate crossovers and outcomes
            for i in range(25, len(prices) - 10):
                window = prices[:i]
                future_prices = prices[i:i+10]

                smma20 = self._smma(window, 20)
                smma120 = self._smma(window, min(120, len(window)))

                prev_window = prices[:i-1]
                prev_smma20 = self._smma(prev_window, 20)
                prev_smma120 = self._smma(prev_window, min(120, len(prev_window)))

                # Detect crossover
                signal = None
                if prev_smma20 <= prev_smma120 and smma20 > smma120:
                    signal = "BUY"
                elif prev_smma20 >= prev_smma120 and smma20 < smma120:
                    signal = "SELL"

                if signal:
                    features = self.prepare_features(window, signal)
                    if features:
                        # Calculate if trade was profitable
                        entry_price = prices[i]
                        exit_price = prices[i+9]

                        if signal == "BUY":
                            profitable = 1 if exit_price > entry_price else 0
                        else:
                            profitable = 1 if exit_price < entry_price else 0

                        X.append(features)
                        y.append(profitable)

        if len(X) > 10:
            X = np.array(X)
            y = np.array(y)
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_trained = True

            # Get feature importance
            feature_names = ['returns_5', 'returns_20', 'volatility',
                           'smma20', 'smma120', 'smma_distance',
                           'price_trend', 'signal', 'current_price',
                           'mean_price', 'momentum', 'bid_ask_ratio',
                           'bid_qty', 'ask_qty']
            self.feature_importance = dict(zip(
                feature_names,
                self.model.feature_importances_
            ))

            logger.info(f"Model trained on {len(X)} samples from previous day data")
            print(f"✅ Model trained on {len(X)} real market samples!")
        else:
            logger.info("Insufficient previous day data — using synthetic")
            self.train_with_synthetic_data()

    def train_with_synthetic_data(self):
        """Train model with synthetic data as fallback"""
        np.random.seed(42)
        X = []
        y = []

        for _ in range(500):
            prices = list(np.cumsum(
                np.random.normal(0.1, 1, 150)) + 100)
            features = self.prepare_features(prices, "BUY")
            if features:
                X.append(features)
                y.append(1)

            prices = list(np.cumsum(
                np.random.normal(0, 1, 150)) + 100)
            features = self.prepare_features(prices, "BUY")
            if features:
                X.append(features)
                y.append(0)

            prices = list(np.cumsum(
                np.random.normal(-0.1, 1, 150)) + 100)
            features = self.prepare_features(prices, "SELL")
            if features:
                X.append(features)
                y.append(1)

        X = np.array(X)
        y = np.array(y)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        print("✅ ML model trained with synthetic data!")

    def predict_signal(self, prices, signal_type, ltq_features=None):
        """Predict if crossover signal is profitable"""
        if not self.is_trained:
            self.train_with_synthetic_data()

        features = self.prepare_features(prices, signal_type, ltq_features)
        if features is None:
            return {
                "prediction": "INSUFFICIENT DATA",
                "probability": 0,
                "recommendation": "AVOID",
                "reason": "Not enough price history"
            }

        features_scaled = self.scaler.transform([features])
        probability = self.model.predict_proba(
            features_scaled)[0][1] * 100
        prediction = self.model.predict(features_scaled)[0]

        reason = self._generate_reason(
            features, probability, signal_type)

        return {
            "prediction": "PROFITABLE" if prediction == 1
                         else "AVOID",
            "probability": round(probability, 1),
            "recommendation": "TAKE TRADE" if probability > 65
                            else "AVOID TRADE",
            "reason": reason
        }

    def _generate_reason(self, features, probability, signal_type):
        """Generate human readable reason"""
        returns_5 = features[0]
        returns_20 = features[1]
        volatility = features[2]
        smma_distance = features[5]
        price_trend = features[6]
        momentum = features[10]
        bid_ask_ratio = features[11]

        reasons = []

        if probability > 65:
            if signal_type == "BUY":
                if returns_20 > 1:
                    reasons.append("Strong upward momentum")
                if price_trend > 0:
                    reasons.append("Positive price trend")
                if bid_ask_ratio > 1.2:
                    reasons.append("High buyer interest")
                if smma_distance > 0:
                    reasons.append("SMMA20 above SMMA120")
            else:
                if returns_20 < -1:
                    reasons.append("Strong downward momentum")
                if price_trend < 0:
                    reasons.append("Negative price trend")
                if bid_ask_ratio < 0.8:
                    reasons.append("High seller pressure")
        else:
            if volatility > 3:
                reasons.append("High volatility — risky")
            if abs(returns_5) < 0.1:
                reasons.append("Low momentum — weak signal")
            if abs(smma_distance) < 0.3:
                reasons.append("SMAs too close — false crossover risk")
            if momentum < 0 and signal_type == "BUY":
                reasons.append("Negative short-term momentum")
            if bid_ask_ratio < 1 and signal_type == "BUY":
                reasons.append("More sellers than buyers")

        return " | ".join(reasons) if reasons else "Signal strength insufficient"