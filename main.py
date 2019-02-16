import os
from trader import Trader

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

tr = Trader(api_key, api_secret, 'USDT', 'ETH', 100)
tr.start()
