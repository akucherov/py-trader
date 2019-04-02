from BaseStrategy import BaseStrategy

class SimpleEMAStrategy(BaseStrategy):

    def __init__(self, ema1=7, ema2=25, precision=2, size=60):
        BaseStrategy.__init__(self, precision, size)
        self.ema1 = ema1
        self.ema2 = ema2

    def indicators(self):
        self.ema(self.ema1,'close','ema' + str(self.ema1))
        self.ema(self.ema2,'close','ema' + str(self.ema2))

    def buySignal(self):
        k1 = 'ema' + str(self.ema1)
        k2 = 'ema' + str(self.ema2)
        if len(self.data) > 2:
            s2 = self.data[-3][k1]
            s1 = self.data[-2][k1]
            l2 = self.data[-3][k2]
            l1 = self.data[-2][k2]
            if not (s1 is None or s2 is None or l1 is None or l2 is None):
                return (s2 < l2) and (s1 >= l1)
            else:
                return False
        else:
            return False

    def sellSignal(self):
        k1 = 'ema' + str(self.ema1)
        k2 = 'ema' + str(self.ema2)
        if len(self.data) > 2:
            s2 = self.data[-3][k1]
            s1 = self.data[-2][k1]
            l2 = self.data[-3][k2]
            l1 = self.data[-2][k2]
            if not (s1 is None or s2 is None or l1 is None or l2 is None):
                return (s2 > l2) and (s1 <= l1)
            else:
                return False
        else:
            return False