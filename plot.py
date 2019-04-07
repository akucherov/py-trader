import numpy as np
import pandas as pd
from datetime import datetime
from AltBaseStrategy import BaseStrategy

df = pd.read_csv('./data/2018-1-1-BTCUSDT-5m.csv').take(range(10))

strategy = BaseStrategy(size=10)

for _, row in df.iterrows():
    ts = datetime.fromtimestamp(row['Open time']/1000)
    strategy.capture(ts, row['Open'], row['Close'], row['High'], row['Low'], row['Volume'], row['Number of trades'])


strategy.df.drop(pd.Timestamp('2018-01-01 11:00:00'), inplace=True)
print(strategy.df.shape)
print(strategy.df)
print(strategy.df.index)