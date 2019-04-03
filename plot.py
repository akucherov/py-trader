import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates

df = pd.read_csv('./data/2018-1-1-BTCUSDT-5m.csv').head()

df["Open time"] = df["Open time"]/1000
df["Open time"] = df["Open time"].apply(datetime.fromtimestamp)
df["Open time"] = df["Open time"].apply(mdates.date2num)

ohlc= df[['Open time', 'Open', 'High', 'Low','Close']].copy()

f1, ax = plt.subplots(figsize = (10,10))

print(ohlc.values)

candlestick_ohlc(ax, ohlc.values, width=.6, colorup='green', colordown='red')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.savefig('./data/2018-1-1-BTCUSDT-5m.png')
