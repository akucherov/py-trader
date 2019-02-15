import os
import common
from binance.client import Client
from binance.websockets import BinanceSocketManager
from trader import Trader

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

client = Client(api_key, api_secret)

klines = client.get_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, limit=60)
info = client.get_exchange_info()

symbol = 'ETHUSDT'

if info["symbols"]:
    r = [i for i in info["symbols"] if i["symbol"]==symbol]
    if r:
        bm = BinanceSocketManager(client)
        tr = Trader(
            symbol, 
            r[0]["quotePrecision"], 
            r[0]["baseAssetPrecision"],
            float([i for i in r[0]["filters"] if i["filterType"]=="LOT_SIZE"][0]["stepSize"]),
            common.prec(float([i for i in r[0]["filters"] if i["filterType"]=="PRICE_FILTER"][0]["minPrice"])),
            klines=klines)
        conn_key = bm.start_kline_socket(symbol, tr.monitor, interval=Client.KLINE_INTERVAL_1MINUTE)

        bm.start()


