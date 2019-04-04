import pandas as pd
import plotly.plotly as py
from plotly import figure_factory as FF
from datetime import datetime
import plotly.io as pio
from LinearRegressionStrategy import LinearRegressionStrategy

df = pd.read_csv('./data/2018-1-1-BTCUSDT-5m.csv').take(range(20, 24))

strategy = LinearRegressionStrategy()

for _, row in df.iterrows():
    strategy.capture(row['Open time'], row['Open'], row['Close'], row['High'], row['Low'], row['Volume'], row['Number of trades'])

#print(strategy.local_min)
print(strategy.ts)
print(strategy.pr)
print(strategy.line)

df["Open time"] = df["Open time"]/1000
df["Open time"] = df["Open time"].apply(datetime.fromtimestamp)
df.set_index('Open time', inplace=True)

fig = FF.create_candlestick(df.Open, df.High, df.Low, df.Close, dates=df.index)
fig['layout'].update({
    'title': 'BTC-USDT',
    'width': 1440,
    'height': 860,
    'yaxis': {'title': 'asset price'}})
pio.write_image(fig, './data/2018-1-1-BTCUSDT-5m.png')