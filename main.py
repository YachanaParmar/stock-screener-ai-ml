import time
import logging
import schedule
from bot.api_client import AngelOneClient
from bot.screener import StockScreener
from bot.dashboard import display_dashboard
from config import REFRESH_INTERVAL

logging.basicConfig(
    filename='logs/screener.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def main():
    print("🚀 Starting Stock Screener...")
    print("=" * 50)
    
    # Initialize client
    client = AngelOneClient()
    
    # Login
    if not client.login():
        print("❌ Login failed. Check credentials in config.py")
        return
    
    # Initialize screener
    screener = StockScreener(client)
    refresh_count = 0
    
    print("\n✅ System Ready! Starting screening...\n")
    
    while True:
        try:
            refresh_count += 1
            
            # Screen stocks
            stocks = screener.screen_stocks()
            
            # Display dashboard
            display_dashboard(stocks, refresh_count)
            
            # Wait before next refresh
            print(f"\n⏳ Next refresh in {REFRESH_INTERVAL} seconds...")
            time.sleep(REFRESH_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Screener stopped by user.")
            break
        except Exception as e:
            logging.error(f"Main loop error: {e}")
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()