from BaseStrategy import BaseStrategy

class MACDRSIStrategy(BaseStrategy):

    def __init__(self, rsi=14, level1=30, level2=70, level3=0.5, precision=2, size=60):
        BaseStrategy.__init__(self, precision, size)
        self.rw = rsi
        self.level1 = level1
        self.level2 = level2
        self.level3 = level3

    def indicators(self):
        self.ema(12,'close','ema12')
        self.ema(26,'close','ema26')
        self.rsi(self.rw,'close','rsi')
        self.macd(9,'ema12','ema26')

    def buySignal(self):
        if len(self.data) > 3:
            m3 = self.data[-4]['macd']
            m2 = self.data[-3]['macd']
            m1 = self.data[-2]['macd']
            h = self.data[-2]['macdh']
            r = self.data[-2]['rsi']
            if not (m1 is None or m2 is None or m3 is None or r is None or h is None):
                return (h < 0) and (m3 >= m2) and (m2 <= m1) and (r <= self.level1)
            else:
                return False
        else:
            return False

    def sellSignal(self):
        if len(self.data) > 3:
            m3 = self.data[-4]['macd']
            m2 = self.data[-3]['macd']
            m1 = self.data[-2]['macd']
            r = self.data[-2]['rsi']
            if not (m1 is None or m2 is None or m3 is None or r is None):
                return (r >= self.level2 and m3 <= m2 and m2 >= m1) or (m2 - m1 > self.level3)
            else:
                return False
        else:
            return False