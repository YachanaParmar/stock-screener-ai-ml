# 🚀 AI/ML Stock Market Screening and Analysis System

A real-time stock market screening and analysis system built with Python, 
integrating Angel One Smart API with AI/ML-based crossover signal prediction.

---

## 📋 Features

- ✅ Real-time NSE stock screening (LTP ₹30-₹500)
- ✅ Liquidity filter (Bid/Ask Quantity > 10 Lakh)
- ✅ SMMA (20) and SMMA (120) calculation
- ✅ Automatic crossover signal detection (BUY/SELL)
- ✅ AI/ML prediction using Random Forest Classifier
- ✅ Signal probability and success rate display
- ✅ Reason for accepting/rejecting trade signals
- ✅ Exchange Traded Quantity (5min, 20min, 60min)
- ✅ Average LTP (20min, 60min)
- ✅ Live Market Depth (Bid/Ask Price & Quantity)
- ✅ Auto-refreshing real-time dashboard
- ✅ Complete logging system

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Broker API:** Angel One Smart API
- **ML Framework:** Scikit-learn (Random Forest)
- **Data Processing:** Pandas, NumPy
- **Dashboard:** Terminal-based real-time display
- **Authentication:** PyOTP (TOTP)

---

## 📁 Project Structure
stock_screener/
├── bot/
│ ├── init.py
│ ├── api_client.py # Angel One API wrapper
│ ├── screener.py # Stock screening logic
│ ├── indicators.py # SMMA calculation
│ ├── ml_model.py # AI/ML signal prediction
│ └── dashboard.py # Real-time display
├── logs/
│ └── screener.log # Application logs
├── config.py # Configuration & credentials
├── main.py # Entry point
└── README.md
---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.x
- Angel One trading account
- Smart API access enabled

### Step 1 — Clone/Download the project

```bash
cd stock_screener
```

### Step 2 — Install dependencies

```bash
pip install smartapi-python pandas numpy scikit-learn 
pip install pyotp requests logzero schedule flask
```

### Step 3 — Configure credentials

Open `config.py` and fill in your Angel One credentials:

```python
API_KEY = "your_api_key"
CLIENT_ID = "your_client_id"    # e.g. AACK710335
PASSWORD = "your_mpin"
TOTP_KEY = "your_totp_secret"
```

### Step 4 — Run the application

```bash
python main.py
```

---

## 🔑 Getting Angel One Smart API Credentials

1. Create account at **angelone.in**
2. Go to **smartapi.angelbroking.com**
3. Login with your Client ID and MPIN
4. Click **"Create App"**
5. Get your **API Key**
6. Enable **TOTP** in Angel One app settings
7. Copy the **TOTP secret key**

---

## 📊 How It Works

### Stock Screening
1. Fetches all NSE-listed stocks
2. Filters stocks with LTP between ₹30-₹500
3. Applies liquidity filter (Bid/Ask > 10 Lakh)

### SMMA Calculation
- **SMMA(20):** Short-term smoothed moving average
- **SMMA(120):** Long-term smoothed moving average
- **Buy Signal:** SMMA(20) crosses above SMMA(120)
- **Sell Signal:** SMMA(20) crosses below SMMA(120)

### AI/ML Analysis
- Uses **Random Forest Classifier** trained on market patterns
- Evaluates each crossover signal
- Provides **probability score** (0-100%)
- Recommends **TAKE TRADE** or **AVOID TRADE**
- Explains **reason** for recommendation

---

## 📈 Dashboard Output
================================================================
🚀 STOCK SCREENER & AI/ML ANALYSIS DASHBOARD
📅 2026-08-08 10:30:00 | 🔄 Refresh #5 | 📊 Stocks: 12
Symbol LTP SMMA20 SMMA120 Signal ML Pred Prob
RELIANCE 245.50 244.20 242.10 🟢 BUY PROFITABLE 72.5%
TATASTEEL 98.75 98.20 99.10 🔴 SELL AVOID 45.2%
---

## 🤖 AI/ML Model Details

- **Algorithm:** Random Forest Classifier (100 estimators)
- **Features:** Price momentum, volatility, SMMA distance, trend
- **Training:** Synthetic market data with trend patterns
- **Threshold:** 65% probability for TAKE TRADE recommendation

---

## ⚠️ Disclaimer

This tool is for educational purposes only. 
Stock market trading involves financial risk. 
Always do your own research before trading.

---

## 👩‍💻 Author

**Yachana Parmar**
- GitHub: github.com/YachanaParmar
- Email: yachanapanwar5@gmail.com