from functools import reduce
from collections import defaultdict

class BaseStrategy:

    data = []

    def __init__(self, precision=2, size=60):
        self.precision = precision
        self.size = size

    def capture(self, ts, o, c, h, l, v, t):
        rec = defaultdict(lambda:None)
        rec['ts'] = int(ts)
        rec['open'] = float(o)
        rec['close'] = float(c)
        rec['high'] = float(h)
        rec['low'] = float(l)
        rec['volume'] = float(v)
        rec['trades'] = int(t)
        if len(self.data) and self.data[-1]['ts'] == rec['ts']:
            self.data[-1] = rec
        else:
            self.data.append(rec)

        if len(self.data) > self.size: self.data.pop(0)

        self.indicators()

    def indicators(self):
        self.ema(7,'close','ema7')
        self.ema(12,'close','ema12')
        self.ema(26,'close','ema26')
        self.rsi(14,'close','rsi6')
        self.macd(9,'ema12','ema26')

    def buySignal(self):
        return False

    def sellSignal(self):
        return False

    def ema(self, w, s, r):
        d = self.data
        p = self.precision * 2
        if len(d) >= w:
            if d[-2][r] is None:
                if not reduce(lambda x,y: x if x is None else y, [v[s] for v in d[-w:]]) is None:
                    d[-1][r] = round(sum([r[s] for r in d[-w:]]) / float(w), p)
            else:
                c = 2.0 / (w + 1) 
                d[-1][r] = round(c*(d[-1][s] - d[-2][r]) + d[-2][r], p)
    
    def macd(self, w, k1, k2):
        d = self.data
        p = self.precision * 2
        if not (d[-1][k1] is None or d[-1][k2] is None):
            d[-1]['macd'] = round(d[-1][k1] - d[-1][k2], p)
            self.ema(w,'macd','macds')
            if not (d[-1]['macd'] is None or d[-1]['macds'] is None):
                d[-1]['macdh'] = round(d[-1]['macd'] - d[-1]['macds'], p)

    def rsi(self, w, s, r):
        d = self.data
        p = self.precision * 2
        if len(d) > w:
            k1 = 'gain' + str(w)
            k2 = 'loss' + str(w)
            if d[-2][k1] is None and d[-2][k2] is None:
                c1 = [] 
                c2 = []
                prev = d[-w-1][s]
                for k in d[-w:]:
                    if k[s] >= prev: c1.append(k[s] - prev)
                    else: c2.append(prev - k[s])
                    prev = k[s]
                gain = sum(c1) / w
                loss = sum(c2) / w
            else:
                changes =  d[-1][s] - d[-2][s]
                if changes >= 0:
                    gain = round((d[-2][k1] * (w - 1) + changes) / w, p)
                    loss = round((d[-2][k2] * (w - 1)) / w, p)
                else:
                    gain = round((d[-2][k1] * (w - 1)) / w, p)
                    loss = round((d[-2][k2] * (w - 1) - changes) / w, p)

            d[-1][k1] = round(gain, p)
            d[-1][k2] = round(loss, p)
            d[-1][r] = round(100 - (100 / (1 + gain/loss)), p)