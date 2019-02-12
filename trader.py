from collections import namedtuple 

StockRec = namedtuple('StockRec' , 'ts open close high low volume ema3, ema7 ema12 ema26 macd macds macdh') 

class Trader:

    def __init__(self):
        self.data = []

    def monitor(self, msg):
        if msg['e'] == 'kline':
            k = msg['k']
            rec = StockRec(k['t'],float(k['o']),float(k['c']),float(k['h']),float(k['l']),float(k['v']),None,None,None,None,None,None,None)
            if len(self.data) and self.data[-1].ts == rec.ts:
                self.data[-1] = rec
            else:
                self.data.append(rec)

            self.ema(3,'ema3')
            self.ema(7,'ema7')
            self.ema(12,'ema12')
            self.ema(26,'ema26')

            print(self.data[-1])

    def ema(self, window, key):
        if len(self.data) >= window:
            if getattr(self.data[-2], key):
                c = 2.0 / (window + 1) 
                setattr(self.data[-1], key, c*(self.data[-1].close - getattr(self.data[-2], key)) + getattr(self.data[-2], key))
            else: 
                setattr(self.data[-1], key, sum([r.close for r in self.data[-window:]]) / float(window))
