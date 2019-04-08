import numpy as np
import pandas as pd
from datetime import datetime
from SupportLinesStrategy import SupportLinesStrategy

df = pd.read_csv('./data/2018-1-1-BTCUSDT-5m.csv').take(range(800))

strategy = SupportLinesStrategy(n=8, size=100)

for _, row in df.iterrows():
    ts = datetime.fromtimestamp(row['Open time']/1000)
    strategy.capture(ts, row['Open'], row['Close'], row['High'], row['Low'], row['Volume'], row['Number of trades'])


print(strategy.df)