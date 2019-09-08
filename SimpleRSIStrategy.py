import numpy as np
from scipy.signal import argrelextrema
from AltBaseStrategy import BaseStrategy

class SimpleRSIStrategy(BaseStrategy):

    def __init__(self, rsi=14, buy=28, sell=80, size=288):
        BaseStrategy.__init__(self, size)
        self.rsi = rsi
        self.rsikey = "RSI"+str(rsi)
        self.buyline = buy
        self.sellline = sell

    def indicators(self):
        self.df = self.RSI(self.df, period=self.rsi)
        if (self.buyTS is None):
            self.df['buy'] = \
                (self.df[self.rsikey].shift(2) < self.buyline) & \
                (self.df[self.rsikey].shift(1) < self.buyline) & \
                (self.df[self.rsikey] > self.buyline)
        else:
            self.df['sell'] = (self.df[self.rsikey] > self.sellline)

        self.fillna('buy', False)
        self.fillna('sell', False)

    def buySignal(self):
        return not self.df is None \
            and self.buyTS is None \
            and 'buy' in self.df.columns.values \
            and self.df.iloc[-1]['buy']

    def sellSignal(self):
        return not self.df is None \
            and not self.buyTS is None \
            and 'sell' in self.df.columns.values \
            and self.df.iloc[-1]['sell']

    def fillna(self, column, value):
        if column in self.df.columns.values:
            self.df[column].fillna(value, inplace=True)
        else:
            self.df[column] = value