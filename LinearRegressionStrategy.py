import numpy as np 
from BaseStrategy import BaseStrategy

class LinearRegressionStrategy(BaseStrategy):
    ts = []
    pr = []
    line = None
    prediction = None
    buy = False
    sell = False

    def __init__(self, acc_buy=1, acc_sell=1, precision=2, size=60):
        BaseStrategy.__init__(self, precision, size)
        self.acc_buy = acc_buy
        self.acc_sell = acc_sell

    def indicators(self):
        self.buy = False
        self.sell = False
        if len(self.data) > 2 and (len(self.ts) == 0 or self.ts[-1] != self.data[-3]['ts']):
            self.ts.append(self.data[-3]['ts'])
            self.pr.append(self.data[-3]['close'])
            if len(self.ts) > 1:
                self.line = self.regression(np.array(self.ts), np.array(self.pr))
                self.prediction = self.line[0] + self.line[1] * self.data[-2]['ts']
                if self.line[1] < 0 and round((self.data[-2]['close']/self.prediction - 1) * 100, 2) > self.acc_buy:
                    self.line = None
                    self.prediction = None
                    self.ts = []
                    self.pr = []
                    self.ts.append(self.data[-3]['ts'])
                    self.pr.append(self.data[-3]['close'])
                    self.buy = True
                elif self.line[1] > 0 and round((self.data[-2]['close']/self.prediction - 1) * 100, 2) < self.acc_sell:
                    self.line = None
                    self.prediction = None
                    self.ts = []
                    self.pr = []
                    self.ts.append(self.data[-3]['ts'])
                    self.pr.append(self.data[-3]['close'])
                    self.sell = True

    def buySignal(self):
        return self.buy

    def sellSignal(self):
        return self.sell

    def regression(self, x, y):  
        m_x, m_y = np.mean(x), np.mean(y) 
  
        SS_xy = np.sum((x - m_x)*(y - m_y)) 
        SS_xx = np.sum((x - m_x)*(x - m_x))
  
        b_1 = SS_xy / SS_xx 
        b_0 = m_y - b_1*m_x 
  
        return(b_0, b_1) 