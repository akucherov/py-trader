import numpy as np
import pandas as pd
from datetime import datetime
from scipy.signal import argrelextrema
from AltBaseStrategy import BaseStrategy

class SupportLinesStrategy(BaseStrategy):
    def __init__(self, n=8, size=288):
        BaseStrategy.__init__(self, size)
        self.n = n
        self.delta = 1

    def indicators(self):
        self.df['min'] = self.df.iloc[argrelextrema(self.df.close.values, np.less_equal, order=self.n)[0]]['close']
        self.df['max'] = self.df.iloc[argrelextrema(self.df.close.values, np.greater_equal, order=self.n)[0]]['close']
        self.mins, self.min_lines = self.supportLines(self.df['min'].dropna().items())
        self.maxs, self.max_lines = self.supportLines(self.df['max'].dropna().items())
            
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