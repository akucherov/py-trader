import numpy as np
import pandas as pd
from datetime import datetime
from scipy.signal import argrelextrema
from AltBaseStrategy import BaseStrategy

class SupportLinesStrategy(BaseStrategy):
    buy = None
    sell = None
    precision = 4

    def __init__(self, n=36, k1=1, k2=1, k3=1, size=288):
        BaseStrategy.__init__(self, size)
        self.n = n
        self.delta = k1
        self.buyDelta = k2
        self.sellDelta = k3

    def indicators(self):
        #self.df['min'] = self.df.iloc[argrelextrema(self.df.close.values, np.less_equal, order=self.n)[0]]['close']
        #self.df['max'] = self.df.iloc[argrelextrema(self.df.close.values, np.greater_equal, order=self.n)[0]]['close']
        
        self.mins, self.min_lines = self.supportLines(self.df['min'].dropna().items())
        self.maxs, self.max_lines = self.supportLines(self.df['max'].dropna().items())

        ts = self.df.tail(1).index[0]
        x = ts.timestamp()
        if len(self.maxs) > 0 and len(self.mins) > 0:
            bb0, bb1 = self.maxs[-1]
            bpp = bb0 + bb1*x
            sb0, sb1 = self.mins[-1]
            spp = sb0 + sb1*x
            rp = self.df.tail(1)['close'][0]

            if sb1 > 0 and round(((rp - bpp)/bpp)*100, 2) > self.buyDelta and bpp > spp:
                self.addBuyPoint(ts, rp)

            if round(((spp - rp)/rp)*100, 2) > self.sellDelta:
                self.addSellPoint(ts, rp)                         

    def buySignal(self):
        return not self.buy is None and self.df.tail(1).index[0] == self.buy.tail(1).index[0]

    def sellSignal(self):
        return not self.sell is None and self.df.tail(1).index[0] == self.sell.tail(1).index[0]

    def addBuyPoint(self, ts, price):
        rec = pd.DataFrame(
            data=[[ts,price]],
            columns=['ts','price'])
        rec.set_index('ts', inplace=True)
        if self.buy is None: self.buy = rec
        else: self.buy = pd.concat([self.buy, rec])

    def addSellPoint(self, ts, price):
        rec = pd.DataFrame(
            data=[[ts,price]],
            columns=['ts','price'])
        rec.set_index('ts', inplace=True)
        if self.sell is None: self.sell = rec
        else: self.sell = pd.concat([self.sell, rec])
            
    def supportLines(self, prices):
        k = []
        lines = []
        xs = []   
        ys = []
        n = 0

        for ts, y in prices:
            x = ts.timestamp()
            if len(xs) < 2:
                xs.append(x)
                ys.append(y)
            else:
                b_0, b_1 = self.regression(np.array(xs), np.array(ys))
                py = b_0 + b_1 * x
                if len(k) > n: k[n] = [b_0,b_1]
                else: k.append([b_0,b_1])
                d = abs(round((y/py-1)*100,2))
                if d > self.delta:
                    lines.append([[pd.Timestamp.utcfromtimestamp(xs[0]), b_0 + b_1 * xs[0]], [ts, py]])
                    xs = [x]
                    ys = [y]
                    n += 1
                else:
                    xs.append(x)
                    ys.append(y)
        if len(xs) > 1:
            b_0, b_1 = self.regression(np.array(xs), np.array(ys))
            k.append([b_0,b_1])
            lines.append([[pd.Timestamp.utcfromtimestamp(xs[0]), b_0 + b_1 * xs[0]], [pd.Timestamp.utcfromtimestamp(xs[-1]), b_0 + b_1 * xs[-1]]])
        return (k, lines)

    def regression(self, x, y):  
        m_x, m_y = np.mean(x), np.mean(y) 
  
        SS_xy = np.sum((x - m_x)*(y - m_y)) 
        SS_xx = np.sum((x - m_x)*(x - m_x))
  
        b_1 = SS_xy / SS_xx 
        b_0 = m_y - b_1*m_x 
  
        return(b_0, b_1)