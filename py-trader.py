import os
from binance.client import Client
from binance.websockets import BinanceSocketManager

def process_message(msg):
    print(msg)

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

client = Client(api_key, api_secret)
bm = BinanceSocketManager(client)
conn_key = bm.start_kline_socket('BTCUSDT', process_message, interval=Client.KLINE_INTERVAL_1MINUTE)

bm.start()

