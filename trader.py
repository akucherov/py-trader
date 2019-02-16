import common
from binance.client import Client
from binance.websockets import BinanceSocketManager
from collections import defaultdict
from functools import reduce
from math import floor 

class Trader:

    def __init__(self, key, secret, baseQuote, asset, orderSize, interval=Client.KLINE_INTERVAL_1MINUTE):
        self.client = Client(key, secret)
        self.symbol = asset + baseQuote
        self.baseQuote = baseQuote
        self.asset = asset
        self.orderSize = orderSize
        self.interval = interval

        # Account balance
        acc = self.client.get_asset_balance(baseQuote)
        self.balance = float(acc['free'])

        # Get step size, precision and others
        info = self.client.get_exchange_info()
        r = [i for i in info["symbols"] if i["symbol"]==self.symbol]
        self.quoteP = r[0]["quotePrecision"]
        self.assetP = r[0]["baseAssetPrecision"]
        self.step = float([i for i in r[0]["filters"] if i["filterType"]=="LOT_SIZE"][0]["stepSize"])
        self.precision = common.prec(float([i for i in r[0]["filters"] if i["filterType"]=="PRICE_FILTER"][0]["minPrice"]))

        # Prepare initial state
        self.data = []
        self.status = 1
        self.ts = 0
        self.orders = []
        self.orderLifeTime = 0

        klines = self.client.get_klines(symbol=self.symbol, interval=self.interval, limit=60)
        if not klines is None:
            for k in klines:
                rec = defaultdict(lambda:None)
                rec['ts'] = k[0]
                rec['close'] = float(k[4])
                self.data.append(rec)
                self.indicators()

    def start(self):
        self.bm = BinanceSocketManager(self.client)
        self.conn_key = self.bm.start_kline_socket(self.symbol, self.monitor, interval=self.interval)
        self.bm.start()

    def monitor(self, msg):
        if msg['e'] == 'kline':
            k = msg['k']
            rec = defaultdict(lambda:None)
            rec['ts'] = k['t']
            rec['close'] = float(k['c'])
            if len(self.data) and self.data[-1]['ts'] == rec['ts']:
                self.data[-1] = rec
            else:
                self.data.append(rec)
                if self.status == 2: self.orderLifeTime += 1
                if len(self.data) > 1 and self.data[-2]['ts'] != self.data[-1]['ts']:
                    print(
                        "Price: %4.2f, current balance: %5.2f, ema(7): %s, ema(25): %s, macd: %s, macdh: %s" % 
                        (self.data[-2]['close'], self.balance, self.data[-2]['ema7'], self.data[-2]['ema25'], self.data[-2]['macd'], self.data[-2]['macdh']))

            if len(self.data) > 60: self.data.pop(0)

            self.indicators()

            if self.status == 1 and self.data[-1]['ts'] != self.ts and self.buySignal():
                self.buy() 
                self.status = 2

            if self.status == 2 and self.data[-1]['ts'] != self.ts and self.sellSignal():
                self.sell()
                self.status = 1


    def indicators(self):
        self.ema(7,'close','ema7')
        self.ema(12,'close','ema12')
        self.ema(25,'close','ema25')
        self.ema(26,'close','ema26')
        self.macd()

    def buy(self):
        self.ts = self.data[-1]['ts']
        order = defaultdict(lambda:None)
        order['buy'] = self.ts
        order['buyPrice'] = self.data[-1]['close']
        order['buyVolume'] = self.orderSize / order['buyPrice']
        self.balance -= self.orderSize
        self.orders.append(order)

        print("Buy order: %4.2f" % (order['buyPrice']))

    def sell(self):
        self.ts = self.data[-1]['ts']
        self.orders[-1]['sell'] = self.ts
        self.orders[-1]['sellPrice'] = self.data[-1]['close']
        self.orders[-1]['sellResult'] = self.orders[-1]['buyVolume'] * self.data[-1]['close']
        self.orders[-1]['profit'] = self.orders[-1]['sellResult'] - self.orderSize
        self.balance = round(self.balance + self.orders[-1]['sellResult'], self.quoteP)
        self.orderLifeTime = 0

        print("Sell order: %4.2f, profit: %4.2f" % (self.orders[-1]['sellPrice'], self.orders[-1]['profit']))

    def buySignal(self):
        if len(self.data) > 2:
            h1 = self.data[-2]['macdh']
            h2 = self.data[-3]['macdh']
            ema7 = self.data[-2]['ema7']
            ema25 = self.data[-2]['ema25']
            if not (h1 is None or h2 is None or ema7 is None or ema25 is None):
                return h1 >= 0 and h2 < 0 and ema7 <= ema25
            else:
                return False
        else:
            return False

    def sellSignal(self):
        if len(self.data) > 2:
            macd1 = self.data[-2]['macd']
            macd2 = self.data[-3]['macd']
            if not (macd1 is None or macd2 is None):
                return (self.orderLifeTime < 9 and macd2 > macd1) or (self.orderLifeTime >= 9 and macd2 >= macd1)
            else:
                return False
        else:
            return False

    def valueByQuote(self, quote, price):
        return round(floor((quote / price) / self.step) * self.step, self.assetP)

    def ema(self, window, s, r):
        if len(self.data) >= window:
            if self.data[-2][r] is None:
                if not reduce(lambda x,y: x if x is None else y, [v[s] for v in self.data[-window:]]) is None:
                    self.data[-1][r] = round(sum([r[s] for r in self.data[-window:]]) / float(window), self.precision)
            else:
                c = 2.0 / (window + 1) 
                self.data[-1][r] = round(c*(self.data[-1][s] - self.data[-2][r]) + self.data[-2][r], self.precision)
                
    
    def macd(self):
        if not (self.data[-1]['ema12'] is None or self.data[-1]['ema26'] is None):
            self.data[-1]['macd'] = round(self.data[-1]['ema12'] - self.data[-1]['ema26'], self.precision)
            self.ema(9,'macd','macds')
            if not (self.data[-1]['macd'] is None or self.data[-1]['macds'] is None):
                self.data[-1]['macdh'] = round(self.data[-1]['macd'] - self.data[-1]['macds'], self.precision)
