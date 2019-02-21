import os
import sys
from trader import Trader

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

quote = sys.argv[1] if len(sys.argv) > 1 else "USDT"
assetsConfig = sys.argv[2] if len(sys.argv) > 2 else "assets.txt"
live = sys.argv[3] == 'live' if len(sys.argv) > 3 else False

Trader(api_key, api_secret, quote, assetsConfig, not live).start()
