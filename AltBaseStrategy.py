import numpy as np
import pandas as pd

class BaseStrategy:

    df = None

    def __init__(self, size=600):
        self.size = size

    def capture(self, ts, o, c, h, l, v, t):
        rec = pd.DataFrame(
            data=[[pd.Timestamp(ts),float(o),float(c),float(h),float(l),float(v),int(t)]],
            columns=['ts','open','close','high','low','volume','trades'])
        rec.set_index('ts', inplace=True)
        if self.df is None:
            self.df = rec
        else:
            self.df = pd.concat([self.df, rec])

        self.indicators()

    def indicators(self):
        pass

    def buySignal(self):
        return False

    def sellSignal(self):
        return False
