import os
import sys
from trader import Trader

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

quote = sys.argv[1] if len(sys.argv) > 1 else "USDT"
assetsConfig = sys.argv[2] if len(sys.argv) > 2 else "assets.txt"

f = open(assetsConfig, "r")
line = f.readline()
f.close()

asset = line.split()

Trader(api_key, api_secret, quote, asset[0], float(asset[1]), 
            interval=asset[2],
            buySignalStep=float(asset[3]),
            sellSignalInitPeriod=int(asset[4]),
            sellSignalInitStep=float(asset[5]),
            sellSignalStep=float(asset[6])).start()
