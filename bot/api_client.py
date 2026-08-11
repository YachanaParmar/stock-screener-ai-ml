import requests
import logging
from SmartApi import SmartConnect
import pyotp
from config import API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY

logging.basicConfig(
    filename='logs/screener.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

class AngelOneClient:
    def __init__(self):
        self.smart_api = SmartConnect(api_key=API_KEY)
        self.auth_token = None
        self.feed_token = None

    def login(self):
        try:
            totp = pyotp.TOTP(TOTP_KEY).now()
            data = self.smart_api.generateSession(
                CLIENT_ID, PASSWORD, totp
            )
            self.auth_token = data['data']['jwtToken']
            self.feed_token = self.smart_api.getfeedToken()
            logger.info("Login successful")
            print("✅ Login successful!")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            print(f"❌ Login failed: {e}")
            return False

    def get_all_nse_stocks(self):
        try:
            url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            response = requests.get(url)
            data = response.json()
            nse_stocks = [
                stock for stock in data
                if stock.get('exch_seg') == 'NSE'
                and stock.get('instrumenttype') == ''
                and '-EQ' in stock.get('symbol', '')
            ]
            logger.info(f"Fetched {len(nse_stocks)} NSE stocks")
            return nse_stocks
        except Exception as e:
            logger.error(f"Error fetching stocks: {e}")
            return []

    def get_ltp(self, symbol_token, symbol):
        try:
            data = self.smart_api.ltpData(
                "NSE", symbol, symbol_token
            )
            return data['data']['ltp']
        except Exception as e:
            logger.error(f"Error getting LTP for {symbol}: {e}")
            return None

    def get_market_depth(self, symbol_token, symbol):
        try:
            data = self.smart_api.ltpData(
                "NSE", symbol, symbol_token
            )
            ltp_info = data.get('data', {})
            return {
                'totBuyQuan': ltp_info.get('totBuyQuan', 9999999),
                'totSellQuan': ltp_info.get('totSellQuan', 9999999),
                'buyunfulfilled': [{'price': ltp_info.get('ltp', 0), 'quantity': ltp_info.get('totBuyQuan', 0)}],
                'sellunfulfilled': [{'price': ltp_info.get('ltp', 0), 'quantity': ltp_info.get('totSellQuan', 0)}]
            }
        except Exception as e:
            logger.error(f"Error getting depth for {symbol}: {e}")
            return None

    def get_candle_data(self, symbol_token, symbol, interval="FIVE_MINUTE"):
        try:
            from datetime import datetime, timedelta
            to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            from_date = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
            params = {
                "exchange": "NSE",
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            data = self.smart_api.getCandleData(params)
            return data['data']
        except Exception as e:
            logger.error(f"Error getting candle data for {symbol}: {e}")
            return []