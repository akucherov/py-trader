import numpy as np
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
        self.mins = []
        self.maxs = []

        min_x = []
        min_y = []
        min_n = 0
        for ts, y in self.df['min'].dropna().items():
            x = ts.timestamp()
            if len(min_x) < 2:
                min_x.append(x)
                min_y.append(y)
            else:
                b_0, b_1 = self.regression(np.array(min_x), np.array(min_y))
                if len(self.mins) > min_n: self.mins[min_n] = [b_0,b_1]
                else: self.mins.append([b_0,b_1])
                py = b_0 + b_1 * x
                d = abs(round((y/py-1)*100,2))
                if d > self.delta:
                    min_x = [x]
                    min_y = [y]
                    min_n += 1
                else:
                    min_x.append(x)
                    min_y.append(y)

            
                

    def regression(self, x, y):  
        m_x, m_y = np.mean(x), np.mean(y) 
  
        SS_xy = np.sum((x - m_x)*(y - m_y)) 
        SS_xx = np.sum((x - m_x)*(x - m_x))
  
        b_1 = SS_xy / SS_xx 
        b_0 = m_y - b_1*m_x 
  
        return(b_0, b_1)