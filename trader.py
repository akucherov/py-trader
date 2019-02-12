from collections import namedtuple 

StockRec = namedtuple('StockRec' , 'ts open close high low volume') 

class Trader:

    def __init__(self):
        self.data = []

    def monitor(self, msg):
        if msg['e'] == 'kline':
            k = msg['k']
            rec = StockRec(k['t'],float(k['o']),float(k['c']),float(k['h']),float(k['l']),float(k['v']))
            if len(self.data) and self.data[-1].ts == rec.ts:
                self.data[-1] = rec
            else:
                self.data.append(rec)

            print(self.data)