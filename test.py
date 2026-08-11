from SmartApi import SmartConnect
import pyotp
import requests
from config import API_KEY, CLIENT_ID, PASSWORD, TOTP_KEY

smart = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_KEY).now()
smart.generateSession(CLIENT_ID, PASSWORD, totp)

url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
data = requests.get(url).json()
stocks = [s for s in data if s.get('exch_seg')=='NSE' and '-EQ' in s.get('symbol','')][:5]

for s in stocks:
    try:
        ltp_data = smart.ltpData('NSE', s['symbol'], s['token'])
        ltp = ltp_data['data']['ltp']
        print(f"{s['symbol']} | LTP: {ltp}")
    except Exception as e:
        print(f"{s['symbol']} Error: {e}")