from AltBaseStrategy import BaseStrategy

class RSICumMaxStrategy(BaseStrategy):
    

    def __init__(self, rsi=14, k1=30, k2=0.99, size=288):
        BaseStrategy.__init__(self, size)
        self.rsi = rsi
        self.k1 = k1
        self.k2 = k2

    def indicators(self):
        self.df = self.RSI(self.df, period=14)
        if not self.buyTS is None:
            if 'CUMMAX' in self.df.columns.values: self.df.drop('CUMMAX', axis=1, inplace=True)
            self.df['CUMMAX'] = self.df['Close'].cummax() * 0.99