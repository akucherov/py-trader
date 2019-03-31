import os
import sys
import pandas as pd
from binance.client import Client

api_key = os.environ['BINANCE_API_KEY']
api_secret = os.environ['BINANCE_API_SECRET']

symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
interval = sys.argv[2] if len(sys.argv) > 2 else "5m"
start = sys.argv[3] if len(sys.argv) > 3 else "2018-1-1"
finish = sys.argv[4] if len(sys.argv) > 4 else "now"

bc = Client(api_key, api_secret)

klines = bc.get_historical_klines(symbol, interval, start, finish)

df = pd.DataFrame(
    klines, 
    columns = ['Open time','Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades','r1','r2','r3'])
df.pop('r1')
df.pop('r2')
df.pop('r3')

df.to_csv(path_or_buf="data/"+start+"-"+symbol+"-"+interval+".csv", index=False)