import os
from binance.client import Client
from binance.websockets import BinanceSocketManager
from trader import Trader

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

client = Client(api_key, api_secret)

klines = client.get_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, limit=60)

bm = BinanceSocketManager(client)
tr = Trader(klines=klines)
conn_key = bm.start_kline_socket('ETHUSDT', tr.monitor, interval=Client.KLINE_INTERVAL_1MINUTE)

bm.start()