import numpy as np
from scipy.signal import argrelextrema
from AltBaseStrategy import BaseStrategy

class RSISLStrategy(BaseStrategy):

    def __init__(self, rsi=14, k1=28, k2=13, k3=5, k4=0.99, size=288):
        BaseStrategy.__init__(self, size)
        self.rsi = rsi
        self.rsikey = "RSI"+str(rsi)
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.k4 = k4


    def indicators(self):
        self.df = self.RSI(self.df, period=self.rsi)
        if (self.buyTS is None):
            self.df['buy'] = \
                (self.df[self.rsikey].shift(2) < self.k1) & \
                (self.df[self.rsikey].shift(1) < self.k1) & \
                (self.df[self.rsikey] > self.k1)
        else:
            self.df['ts'] = self.df.index.to_series().apply(lambda x: int(x.timestamp()))
            s = self.df.loc[:self.buyTS].iloc[-self.k3:].iloc[0].name
            d = self.df.loc[s:]['close']
            b = self.df.loc[self.buyTS:self.buyTS]['close']
            self.mins = d.iloc[argrelextrema(d.values, np.less_equal, order=self.k2)[0]].dropna()
            if self.buyTS < self.mins.index[0]: self.mins = b.append(self.mins)
            lmin = self.mins.iloc[:-1] * self.k4
            if lmin.size > 1:
                b0, b1 = self.regression(
                    lmin.index.to_series().apply(lambda x: int(x.timestamp())).to_numpy(), 
                    lmin.to_numpy())
                self.df['pr_price'] = b0 + b1 * self.df['ts']
                self.df['sell'] = (self.df['close'] < self.df['pr_price']) | (self.df[self.rsikey] > 80)
            else:
                self.df['sell'] = False

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

    def regression(self, x, y):  
        mx, my = np.mean(x), np.mean(y) 
  
        SS_xy = np.sum((x - mx)*(y - my)) 
        SS_xx = np.sum((x - mx)*(x - mx))
  
        b1 = SS_xy / SS_xx 
        b0 = my - b1*mx 
  
        return(b0, b1)

    def fillna(self, column, value):
        if column in self.df.columns.values:
            self.df[column].fillna(value, inplace=True)
        else:
            self.df[column] = value