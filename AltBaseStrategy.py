import pandas as pd

class BaseStrategy:

    df = None
    cr = None

    def __init__(self, size=288):
        self.size = size

    def capture(self, ts, o, c, h, l, v, t):
        key = pd.Timestamp(ts)
        rec = pd.DataFrame(
            data=[[key,float(o),float(c),float(h),float(l),float(v),int(t),None,None]],
            columns=['ts','open','close','high','low','volume','trades','min','max'])
        rec.set_index('ts', inplace=True)
        if self.cr is None:
            self.cr = rec
        elif self.cr.tail(1).index[0] == key:
            self.cr = rec
        elif self.df is None:
            self.df = self.cr
            self.cr = rec
        else:
            self.df = pd.concat([self.df, self.cr], sort=False)
            self.cr = rec
            s, _ = self.df.shape
            if s > self.size: 
                self.df.drop(next(self.df.iterrows())[0], inplace=True)
            if s > 2:
                v = float(self.df['close'][-2])
                if self.df.close[-1] > v and self.df.close[-3] > v: self.df['min'][self.df.index[-2]] = v                
                if self.df.close[-1] < v and self.df.close[-3] < v: self.df['max'][self.df.index[-2]] = v
            self.indicators()

    def indicators(self):
        pass

    def buySignal(self):
        return False

    def sellSignal(self):
        return False
