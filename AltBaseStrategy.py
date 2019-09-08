from datetime import datetime
import pandas as pd

class BaseStrategy:

    df = None
    cr = None
    buyTS = None
    sellTS = None

    def __init__(self, size=288):
        self.size = size
        self.precision = 4

    def capture(self, ts, o, c, h, l, v, t):
        key = self.getKey(ts)
        rec = pd.DataFrame(
            data=[[key,float(o),float(c),float(h),float(l),float(v),int(t)]],
            columns=['ts','open','close','high','low','volume','trades'])
        rec.set_index('ts', inplace=True)
        if self.cr is None:
            self.cr = rec
        elif self.cr.iloc[0].name == key:
            self.cr = rec
        elif self.df is None:
            self.df = self.cr
            self.cr = rec
        else:
            self.df = self.df.append(self.cr, sort=False)
            self.cr = rec
            s, _ = self.df.shape
            if not self.buyTS is None and s > self.size and self.buyTS < self.df.iloc[-self.size].name:
                self.df = self.df[self.buyTS:]
            elif s > self.size: 
                self.df = self.df.iloc[-self.size:]
            self.indicators()

    def indicators(self):
        pass

    def buySignal(self):
        return False

    def sellSignal(self):
        return False

    def setBuyTS(self):
        self.buyTS = self.df.iloc[-1].name
        self.sellTS = None

    def setSellTS(self):
        self.sellTS = self.df.iloc[-1].name
        self.buyTS = None

    def getKey(self, ts):
        return ts if isinstance(ts, pd.Timestamp) else pd.Timestamp(datetime.fromtimestamp(int(ts)/1000))
        
    def SMA(self, df, column="close", period=20):
        sma = df[column].rolling(window=period, min_periods=period - 1).mean()
        if 'SMA'+str(period) in df.columns.values: df.drop('SMA'+str(period), axis=1, inplace=True)
        return df.join(sma.to_frame('SMA'+str(period)))

    def EMA(self, df, column="close", period=20):
        ema = df[column].ewm(span=period, min_periods=period - 1).mean()
        if 'EMA'+str(period) in df.columns.values: df.drop('EMA'+str(period), axis=1, inplace=True)
        return df.join(ema.to_frame('EMA'+str(period)))

    def RSI(self, df, column="close", period=14):
        delta = df[column].diff()
        up, down = delta.copy(), delta.copy()

        up[up < 0] = 0
        down[down > 0] = 0

        rUp = up.ewm(com=period - 1, min_periods=period, adjust=True).mean()
        rDown = down.ewm(com=period - 1, min_periods=period, adjust=True).mean().abs()

        rsi = 100 - 100 / (1 + rUp / rDown)    

        if 'RSI'+str(period) in df.columns.values: df.drop('RSI'+str(period), axis=1, inplace=True)
        return df.join(rsi.to_frame('RSI'+str(period)))