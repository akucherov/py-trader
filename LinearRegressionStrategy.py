import numpy as np 
from BaseStrategy import BaseStrategy

class LinearRegressionStrategy(BaseStrategy):
    ts = []
    pr = []
    line = None

    def __init__(self, accuracy=1, precision=2, size=60):
        BaseStrategy.__init__(self, precision, size)
        self.accuracy = accuracy

    def indicators(self):
        if len(self.data) > 1 and (len(self.ts) == 0 or self.ts[-1] != self.data[-2]):
            self.ts.append(self.data[-2]['ts'])
            self.pr.append(self.data[-2]['close'])
            self.line = self.regression(np.array(self.ts), np.array(self.pr))


    def buySignal(self):
        return False

    def sellSignal(self):
        return False

    def regression(self, x, y): 
        n = np.size(x) 
        m_x, m_y = np.mean(x), np.mean(y) 
  
        SS_xy = np.sum(y*x) - n*m_y*m_x 
        SS_xx = np.sum(x*x) - n*m_x*m_x 
  
        b_1 = SS_xy / SS_xx 
        b_0 = m_y - b_1*m_x 
  
        return(b_0, b_1) 