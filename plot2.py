import pandas as pd
import plotly.plotly as py
from plotly import figure_factory as FF
from datetime import datetime
import plotly.io as pio


df = pd.read_csv('./data/2018-1-1-BTCUSDT-5m.csv').tail(100)
df["Open time"] = df["Open time"]/1000
df["Open time"] = df["Open time"].apply(datetime.fromtimestamp)
df.set_index('Open time', inplace=True)

fig = FF.create_candlestick(df.Open, df.High, df.Low, df.Close, dates=df.index)
fig['layout'].update({
    'title': 'BTC-USDT',
    'yaxis': {'title': 'asset price'}})
pio.write_image(fig, './data/2018-1-1-BTCUSDT-5m.png')