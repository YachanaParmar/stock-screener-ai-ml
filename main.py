import time
import logging
import os
from datetime import datetime
from bot.api_client import AngelOneClient
from bot.screener import StockScreener
from bot.dashboard import display_dashboard
from config import REFRESH_INTERVAL

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/screener.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def main():
    print("🚀 Starting AI/ML Stock Screener with Paper Trading...")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    client = AngelOneClient()

    if not client.login():
        print("❌ Login failed. Check credentials in config.py")
        return

    screener = StockScreener(client)
    refresh_count = 0

    print("\n✅ System Ready! Starting live screening...\n")

    while True:
        try:
            refresh_count += 1
            stocks = screener.screen_stocks()
            performance = screener.get_performance()
            display_dashboard(stocks, refresh_count, performance)

            if refresh_count % 10 == 0:
                screener.display_performance()

            screener.collector.save_data()
            print(f"\n⏳ Next refresh in {REFRESH_INTERVAL} seconds...")
            time.sleep(REFRESH_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n👋 Screener stopped by user.")
            print("\n📊 Final Performance Report:")
            screener.display_performance()
            screener.collector.save_data()
            print(f"\n💾 Data saved to: {screener.collector.data_file}")
            print("✅ Use this data tomorrow for model training!")
            break

        except Exception as e:
            logging.error(f"Main loop error: {e}")
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()