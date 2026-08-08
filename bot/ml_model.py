import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class SignalPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, prices, signal_type):
        """Extract features from price data for ML prediction"""
        if len(prices) < 121:
            return None

        df = pd.Series(prices)

        # Price momentum features
        returns_5 = (prices[-1] - prices[-6]) / prices[-6] * 100
        returns_20 = (prices[-1] - prices[-21]) / prices[-21] * 100
        returns_60 = (prices[-1] - prices[-61]) / prices[-61] * 100

        # Volatility
        volatility = np.std(prices[-20:])

        # SMMA values
        smma20 = self._smma(prices, 20)
        smma120 = self._smma(prices, 120)

        # Distance between SMMAss
        smma_distance = ((smma20 - smma120) / smma120) * 100

        # Volume trend (price as proxy)
        price_trend = np.polyfit(range(20), prices[-20:], 1)[0]

        # Signal encoding
        signal_encoded = 1 if signal_type == "BUY" else -1

        features = [
            returns_5,
            returns_20,
            returns_60,
            volatility,
            smma20,
            smma120,
            smma_distance,
            price_trend,
            signal_encoded,
            prices[-1],  # Current price
            np.mean(prices[-20:]),  # 20 period mean
            np.mean(prices[-60:]),  # 60 period mean
        ]

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

    def train_with_synthetic_data(self):
        """Train model with synthetic historical patterns"""
        np.random.seed(42)
        X = []
        y = []

        # Generate synthetic training samples
        for _ in range(1000):
            # Trending market - BUY signal more likely profitable
            prices = list(np.cumsum(
                np.random.normal(0.1, 1, 200)) + 100)
            features = self.prepare_features(prices, "BUY")
            if features:
                X.append(features)
                y.append(1)  # Profitable

            # Ranging market - signals less reliable
            prices = list(np.cumsum(
                np.random.normal(0, 1, 200)) + 100)
            features = self.prepare_features(prices, "BUY")
            if features:
                X.append(features)
                y.append(0)  # Not profitable

            # Downtrending - SELL signal profitable
            prices = list(np.cumsum(
                np.random.normal(-0.1, 1, 200)) + 100)
            features = self.prepare_features(prices, "SELL")
            if features:
                X.append(features)
                y.append(1)  # Profitable

        X = np.array(X)
        y = np.array(y)

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        logger.info("ML model trained successfully")
        print("✅ ML model trained successfully!")

    def predict_signal(self, prices, signal_type):
        """Predict if crossover signal is profitable"""
        if not self.is_trained:
            self.train_with_synthetic_data()

        features = self.prepare_features(prices, signal_type)
        if features is None:
            return {
                "prediction": "INSUFFICIENT DATA",
                "probability": 0,
                "recommendation": "AVOID",
                "reason": "Not enough price history"
            }

        features_scaled = self.scaler.transform([features])
        probability = self.model.predict_proba(
            features_scaled)[0][1]
        prediction = self.model.predict(features_scaled)[0]

        # Generate reason
        reason = self._generate_reason(
            features, probability, signal_type)

        return {
            "prediction": "PROFITABLE" if prediction == 1 
                         else "AVOID",
            "probability": round(probability * 100, 1),
            "recommendation": "TAKE TRADE" if probability > 0.65 
                            else "AVOID TRADE",
            "reason": reason
        }

    def _generate_reason(self, features, probability, signal_type):
        """Generate human readable reason for prediction"""
        returns_5 = features[0]
        returns_20 = features[1]
        volatility = features[3]
        smma_distance = features[6]
        price_trend = features[7]

        reasons = []

        if probability > 0.65:
            if signal_type == "BUY":
                if returns_20 > 2:
                    reasons.append("Strong upward momentum")
                if price_trend > 0:
                    reasons.append("Positive price trend")
                if smma_distance > 0:
                    reasons.append("SMMA20 above SMMA120")
            else:
                if returns_20 < -2:
                    reasons.append("Strong downward momentum")
                if price_trend < 0:
                    reasons.append("Negative price trend")
        else:
            if volatility > 2:
                reasons.append("High volatility - risky")
            if abs(returns_5) < 0.1:
                reasons.append("Low momentum - weak signal")
            if abs(smma_distance) < 0.5:
                reasons.append(
                    "SMAs too close - false crossover risk")

        return " | ".join(reasons) if reasons else \
               "Signal strength insufficient"