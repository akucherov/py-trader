from AltBaseStrategy import BaseStrategy

class RSICumMaxStrategy(BaseStrategy):
    cummax = None

    def __init__(self, rsi=14, k1=30, k2=0.99, size=288):
        BaseStrategy.__init__(self, size)
        self.rsi = rsi
        self.rsikey = "RSI"+str(rsi)
        self.k1 = k1
        self.k2 = k2

    def indicators(self):
        self.df = self.RSI(self.df, period=self.rsi)
        self.df = self.EMA(self.df, period=99)
        self.df['i'] = self.df['EMA99'].diff() > 0
        if not self.buyTS is None:
            if self.cummax is None: self.cummax = self.df.iloc[-1]['close'] * self.k2
            else: self.cummax = max(self.cummax, self.df.iloc[-1]['close'] * self.k2)
        else:
            self.cummax = None

    def buySignal(self):
        if not self.df is None:
            s, _ = self.df.shape
            r = self.df.iloc[-1]
            if self.buyTS is None and s > self.rsi and r[self.rsikey] < self.k1 and r['i']:
                self.cummax = r['close'] * self.k2
                return True
            else:
                return False
        else:
            return False

    def sellSignal(self):
        if not self.cummax is None and self.cummax > self.df.iloc[-1]['close']:
            return True
        else: 
            return False