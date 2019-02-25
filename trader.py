import common
from binance.client import Client
from binance.websockets import BinanceSocketManager
from collections import defaultdict
from functools import reduce
from math import floor
from dateparser import parse
from datetime import datetime

Sec = {'1m':60,'3m':180,'5m':300,'15m':900,'30m':1800,'1h':3600,'2h':7200,'4h':14400,'6h':21600,'8h':28800,'12h':43200,'1d':86400}

class Trader:

    def __init__(self, key, secret, baseQuote, assets, test=True):

        self.client = Client(key, secret)
        self.baseQuote = baseQuote
        self.test = test
        info = self.client.get_exchange_info()
        acc = self.client.get_asset_balance(baseQuote)
        self.quoteBalance = float(acc['free'])

        self.assets = {}

        # Read config file
        f = open(assets, "r")
        for line in f:
            p = line.split()
            symbol =  p[0] + baseQuote
            key = symbol + p[2]
            rec = defaultdict(lambda:None)
            rec['symbol'] = symbol
            rec['asset'] = p[0]
            rec['orderSize'] = float(p[1])
            rec['interval'] = p[2]
            rec['params'] = [float(param) for param in p[3:7]]

            # Asset balance
            acc = self.client.get_asset_balance(p[0])
            rec['balance'] = float(acc['free'])

            # Get step size, precision and others
            r = [i for i in info["symbols"] if i["symbol"]==symbol]
            rec['quoteP'] = r[0]["quotePrecision"]
            rec['assetP'] = r[0]["baseAssetPrecision"]
            rec['step'] = float([i for i in r[0]["filters"] if i["filterType"]=="LOT_SIZE"][0]["stepSize"])
            rec['precision'] = common.prec(float([i for i in r[0]["filters"] if i["filterType"]=="PRICE_FILTER"][0]["minPrice"]))

            # Prepare initial state
            rec['data'] = []
            rec['history'] = []
            rec['status'] = 1
            rec['ts'] = 0
            rec['orders'] = []
            self.assets[key] = rec
            print("%s %s: order step: %s, q pr: %s, a pr: %s, price pr: %s" % (symbol, p[2], rec['step'], rec['quoteP'], rec['assetP'], rec['precision']))
        f.close()

    def start(self):
        self.bm = BinanceSocketManager(self.client)
        for _, asset in self.assets.items():
            klines = self.client.get_klines(symbol=asset['symbol'], interval=asset['interval'], limit=60)
            if not klines is None:
                for k in klines:
                    rec = defaultdict(lambda:None)
                    rec['ts'] = k[0]
                    rec['open'] = float(k[1])
                    rec['close'] = float(k[4])
                    asset['data'].append(rec)
                    self.indicators(asset)
            asset['conn_key'] = self.bm.start_kline_socket(asset['symbol'], self.monitor, interval=asset['interval'])
            if len(asset['data']) > 1: self.print(asset)

        self.bm.start()

    def prepareHistory(self, start, log=True):
        start_ts = datetime.timestamp(parse(start))
        ts = None
        for _, asset in self.assets.items():
            i = Sec[asset['interval']]
            sts = floor(start_ts / i) * i * 1000
            ts = sts if ts is None else min(ts, sts)
            symbol = asset['symbol']
            interval = asset['interval']
            klines = self.client.get_historical_klines(symbol, interval, sts)
            for k in klines:
                msg = {'e':'kline', 'k':{'t':k[0], 's': symbol, 'i': interval, 'o':k[1], 'c':k[4]}}
                asset['history'].append(msg)
                asset['demo_index'] = 0
            if log:
                print("%s %s: %s records, initial balance: %s" % (asset['symbol'], asset['interval'], len(klines), asset['balance']))
        return ts
                    
    def testTrades(self, start_ts):
        ts = start_ts
        while True:
            next_ts = None
            for _, asset in self.assets.items():
                i = asset['demo_index']
                history = asset['history']
                if i < len(history):
                    msg = history[i]
                    t = msg['k']['t']
                    if (t == ts):
                        self.monitor(msg, False)
                        asset['demo_index'] = i+1
                        if i+1 < len(history): t = history[i+1]['k']['t']
                    next_ts = t if next_ts is None else min(next_ts, t)
            if next_ts is None: break
            ts = next_ts

    def testAssetTrades(self, start_ts, asset):
        for msg in asset['history']:self.monitor(msg, False)

    def demo(self, start):
        quoteBalance = self.quoteBalance
        print("%s initial balance %s" % (self.baseQuote, quoteBalance))

        ts = self.prepareHistory(start)
        self.testTrades(ts)

        for _, asset in self.assets.items():
            if asset['status'] == 2: self.sell(asset, False)
        
        print("-----------------------------------")
        print("%s result balance %s" % (self.baseQuote, self.quoteBalance))
        for _, asset in self.assets.items():
            print("%s %s: result balance: %s" % (asset['symbol'], asset['interval'], asset['balance']))

    def tune(self, start, config):
        f = open(config, "r")
        for line in f:
            p = line.split()
            symbol =  p[0] + self.baseQuote
            asset = self.assets[symbol + p[2]]
            asset['testMin'] = [float(min) for min in p[7:11]]
            asset['testMax'] = [float(max) for max in p[11:15]]
            asset['testStep'] = [float(step) for step in p[15:19]]

        self.prepareHistory(start)
        balance = self.quoteBalance

        for _, asset in self.assets.items():
                
            maxProfit = None
            bestParams = []

            for params in common.genParams(asset['testMin'], asset['testMax'], asset['testStep']):
                self.quoteBalance = balance
                asset['data'] = []
                asset['status'] = 1
                asset['ts'] = 0
                asset['orders'] = []
                asset['params'] = params
                asset['balance'] = 0

                for msg in asset['history']: self.monitor(msg, False)
                if asset['status'] == 2: self.sell(asset, False)                                    

                profit = round(self.quoteBalance - balance, asset['quoteP'])
                print("%s : %s" % (params, profit))

                if maxProfit is None or profit >= maxProfit:
                    if bestParams == [] or profit > maxProfit:
                        bestParams = [params]
                    else:
                        bestParams.append(params)
                    maxProfit = profit

            print("The best params:")
            for p in bestParams: print(p)
            print("%s %s : max profit %s" % (asset['symbol'], asset['interval'], maxProfit))
            

    def print(self, asset):
        print(
            "%s %s: price: %s, %s balance: %.8f, %s balance: %.8f, ema(7): %s, ema(25): %s, macd: %s, macdh: %s, rsi(6): %s, rsi(12): %s, rsi(24): %s" % 
            (asset['symbol'], 
             asset['interval'], 
             asset['data'][-2]['close'], 
             self.baseQuote, 
             self.quoteBalance, 
             asset['asset'], 
             asset['balance'], 
             asset['data'][-2]['ema7'], 
             asset['data'][-2]['ema25'], 
             asset['data'][-2]['macd'], 
             asset['data'][-2]['macdh'],
             asset['data'][-2]['rsi6'],
             asset['data'][-2]['rsi12'],
             asset['data'][-2]['rsi24']))

    def monitor(self, msg, log=True):
        if msg['e'] == 'kline':
            k = msg['k']
            asset = self.assets[k['s'] + k['i']]
            data = asset['data']
            rec = defaultdict(lambda:None)
            rec['ts'] = k['t']
            rec['open'] = float(k['o'])
            rec['close'] = float(k['c'])
            if len(data) and data[-1]['ts'] == rec['ts']:
                data[-1] = rec
            else:
                data.append(rec)
                if log and len(data) > 1 and data[-2]['ts'] != data[-1]['ts']:   
                     self.print(asset)
            if len(data) > 60: data.pop(0)

            self.indicators(asset)

            if asset['status'] == 1 and data[-1]['ts'] != asset['ts'] and self.quoteBalance > asset['orderSize'] and self.buySignal(asset):
                self.buy(asset,log) 
                asset['status'] = 2

            if asset['status'] == 2 and data[-1]['ts'] != asset['ts'] and self.sellSignal(asset):
                self.sell(asset,log)
                asset['status'] = 1


    def indicators(self, asset):
        self.ema(asset, 7,'close','ema7')
        self.ema(asset, 12,'close','ema12')
        self.ema(asset, 25,'close','ema25')
        self.ema(asset, 26,'close','ema26')
        self.rsi(asset, 6,'close','rsi6')
        self.rsi(asset, 12,'close','rsi12')
        self.rsi(asset, 24,'close','rsi24')
        self.macd(asset)

    def buy(self, asset, log=True):
        asset['ts'] = asset['data'][-1]['ts']
        order = defaultdict(lambda:None)
        step = asset['step']
        quoteP = asset['quoteP']
        assetP = asset['assetP']
        order['buy'] = asset['ts']
        value = round(floor((asset['orderSize'] / asset['data'][-1]['close']) / step) * step, assetP)

        if self.test:
            quote = round(asset['data'][-1]['close'] * value, quoteP)
            qty = value
            commission = round(value / 1000, assetP)
        else:
            trx = self.client.order_market_buy(symbol=asset['symbol'], quantity=value, newOrderRespType='FULL')

            if trx['status'] == 'FILLED':
                quote = float(trx['cummulativeQuoteQty'])
                qty = float(trx['executedQty'])
                commission = round(sum([float(f['commission']) for f in trx['fills']]), assetP)
            else:
                raise RuntimeError("Market buy order returned unexpected response.")

        order['buyPrice'] = round(quote/qty, asset['precision'])
        order['buyVolume'] = round(qty - commission, assetP)
        order['buyOrderSize'] = quote
        self.quoteBalance = round(self.quoteBalance - quote, quoteP)
        asset['balance'] = round(asset['balance'] + order['buyVolume'], assetP)
        asset['orders'].append(order)
        if log:print("Buy order: %s, order size: %s" % (order['buyPrice'], order['buyOrderSize']))

    def sell(self, asset, log=True):
        asset['ts'] = asset['data'][-1]['ts']
        orders = asset['orders']
        quoteP = asset['quoteP']
        assetP = asset['assetP']
        balance = asset['balance']
        step = asset['step']
        precision = asset['precision']
        orders[-1]['sell'] = asset['ts']
        value = round(floor(balance / step) * step, assetP)

        if self.test:
            quote = round(asset['data'][-1]['close'] * value, quoteP)
            qty = value
            commission = round(quote / 1000, quoteP)
        else:
            trx = self.client.order_market_sell(symbol=asset['symbol'], quantity=value, newOrderRespType='FULL')

            if trx['status'] == 'FILLED':
                quote = float(trx['cummulativeQuoteQty'])
                qty = float(trx['executedQty'])
                commission = round(sum([float(f['commission']) for f in trx['fills']]), quoteP)           
            else:
                raise RuntimeError("Market sell order returned unexpected response.")

        orders[-1]['sellPrice'] = round(quote/qty, precision)
        orders[-1]['sellResult'] = round(quote - commission, quoteP)
        orders[-1]['profit'] = round(orders[-1]['sellResult'] - orders[-1]['buyOrderSize'], quoteP)
        self.quoteBalance = round(self.quoteBalance + orders[-1]['sellResult'], quoteP) 
        asset['balance'] = round(balance - qty, assetP)
        if log:print("Sell order: %s, profit: %s" % (orders[-1]['sellPrice'], orders[-1]['profit']))

    def buySignal(self, asset):
        data = asset['data']
        if len(data) > 2:
            h2 = data[-3]['macdh']
            r1 = data[-2]['rsi6']
            r2 = data[-3]['rsi6']
            (p1, p2) = asset['params'][:2]
            if not (h2 is None or r1 is None or r2 is None):
                return h2 < 0 and r2 < p1 and (r1 -r2) > p2
            else:
                return False
        else:
            return False

    def sellSignal(self, asset):
        data = asset['data']
        if len(data) > 2:
            m1 = data[-2]['macd']
            m2 = data[-3]['macd']
            r1 = data[-2]['rsi6']
            r2 = data[-3]['rsi6']
            (p3, p4) = asset['params'][-2:]
            if not (m1 is None or m2 is None):
                return r2 > p3 and r1 < p3 and (m2 - m1) > p4
            else:
                return False
        else:
            return False


    def ema(self, asset, window, s, r):
        data = asset['data']
        p = asset['precision'] * 2
        if len(data) >= window:
            if data[-2][r] is None:
                if not reduce(lambda x,y: x if x is None else y, [v[s] for v in data[-window:]]) is None:
                    data[-1][r] = round(sum([r[s] for r in data[-window:]]) / float(window), p)
            else:
                c = 2.0 / (window + 1) 
                data[-1][r] = round(c*(data[-1][s] - data[-2][r]) + data[-2][r], p)
                
    
    def macd(self, asset):
        data = asset['data']
        p = asset['precision'] * 2
        if not (data[-1]['ema12'] is None or data[-1]['ema26'] is None):
            data[-1]['macd'] = round(data[-1]['ema12'] - data[-1]['ema26'], p)
            self.ema(asset, 9,'macd','macds')
            if not (data[-1]['macd'] is None or data[-1]['macds'] is None):
                data[-1]['macdh'] = round(data[-1]['macd'] - data[-1]['macds'], p)

    def rsi(self, asset, window, s, r):
        data = asset['data']
        p = asset['precision'] * 2
        if len(data) > window:
            k1 = 'gain' + str(window)
            k2 = 'loss' + str(window)
            if data[-2][k1] is None and data[-2][k2] is None:
                c1 = [] 
                c2 = []
                prev = data[-window-1][s]
                for k in data[-window:]:
                    if k[s] >= prev: c1.append(k[s] - prev)
                    else: c2.append(prev - k[s])
                    prev = k[s]
                gain = sum(c1) / window
                loss = sum(c2) / window
            else:
                changes =  data[-1][s] - data[-2][s]
                if changes >= 0:
                    gain = round((data[-2][k1] * (window - 1) + changes) / window, p)
                    loss = round((data[-2][k2] * (window - 1)) / window, p)
                else:
                    gain = round((data[-2][k1] * (window - 1)) / window, p)
                    loss = round((data[-2][k2] * (window - 1) - changes) / window, p)

            data[-1][k1] = round(gain, p)
            data[-1][k2] = round(loss, p)
            data[-1][r] = round(100 - (100 / (1 + gain/loss)), p)
                
