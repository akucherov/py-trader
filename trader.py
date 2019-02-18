import common
from binance.client import Client
from binance.websockets import BinanceSocketManager
from collections import defaultdict
from functools import reduce
from math import floor 

class Trader:

    def __init__(self, key, secret, baseQuote, assets):

        self.client = Client(key, secret)
        self.baseQuote = baseQuote
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
            rec['buySignalStep'] = float(p[3])
            rec['sellSignalInitPeriod'] = int(p[4])
            rec['sellSignalInitStep'] = float(p[5])
            rec['sellSignalStep'] = float(p[6])

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
            rec['status'] = 1
            rec['ts'] = 0
            rec['orders'] = []
            rec['orderLifeTime'] = 0
            rec['almostBuySignal'] = False
            self.assets[key] = rec
        f.close()

    def start(self):
        self.bm = BinanceSocketManager(self.client)
        for _, asset in self.assets.items():
            klines = self.client.get_klines(symbol=asset['symbol'], interval=asset['interval'], limit=60)
            if not klines is None:
                for k in klines:
                    rec = defaultdict(lambda:None)
                    rec['ts'] = k[0]
                    rec['close'] = float(k[4])
                    asset['data'].append(rec)
                    self.indicators(asset)
            asset['conn_key'] = self.bm.start_kline_socket(asset['symbol'], self.monitor, interval=asset['interval'])
            if len(asset['data']) > 1: self.print(asset)

        self.bm.start()

    def print(self, asset):
        print(
            "%s %s: price: %s, %s balance: %.8f, %s balance: %.8f, ema(7): %s, ema(25): %s, macd: %s, macdh: %s" % 
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
             asset['data'][-2]['macdh']))

    def monitor(self, msg):
        if msg['e'] == 'kline':
            k = msg['k']
            asset = self.assets[k['s'] + k['i']]
            data = asset['data']
            rec = defaultdict(lambda:None)
            rec['ts'] = k['t']
            rec['close'] = float(k['c'])
            if len(data) and data[-1]['ts'] == rec['ts']:
                data[-1] = rec
            else:
                data.append(rec)
                if asset['status'] == 2: asset['orderLifeTime'] += 1
                if len(data) > 1 and data[-2]['ts'] != data[-1]['ts']:   
                    self.print(asset)
            if len(data) > 60: data.pop(0)

            self.indicators(asset)

            if asset['status'] == 1 and data[-1]['ts'] != asset['ts'] and self.quoteBalance > asset['orderSize'] and self.buySignal(asset):
                self.buy(asset) 
                asset['status'] = 2

            if asset['status'] == 2 and data[-1]['ts'] != asset['ts'] and self.sellSignal(asset):
                self.sell(asset)
                asset['status'] = 1


    def indicators(self, asset):
        self.ema(asset, 7,'close','ema7')
        self.ema(asset, 12,'close','ema12')
        self.ema(asset, 25,'close','ema25')
        self.ema(asset, 26,'close','ema26')
        self.macd(asset)

    def buy(self, asset):
        asset['ts'] = asset['data'][-1]['ts']
        order = defaultdict(lambda:None)
        step = asset['step']
        quoteP = asset['quoteP']
        assetP = asset['assetP']
        order['buy'] = asset['ts']
        value = round(floor((asset['orderSize'] / asset['data'][-1]['close']) / step) * step, assetP)


        trx = self.client.order_market_buy(symbol=asset['symbol'], quantity=value, newOrderRespType='FULL')

        if trx['status'] == 'FILLED':
            quote = float(trx['cummulativeQuoteQty'])
            qty = float(trx['executedQty'])
            commision = round(sum([float(f['commission']) for f in trx['fills']]), assetP)
            order['buyPrice'] = round(quote/qty, asset['precision'])
            order['buyVolume'] = round(qty - commision, assetP)
            order['buyOrderSize'] = quote
            self.quoteBalance = round(self.quoteBalance - quote, quoteP)
            asset['balance'] = round(asset['balance'] + order['buyVolume'], assetP)
            asset['orders'].append(order)
            asset['almostBuySignal'] = False
            print("Buy order: %s, order size: %s" % (order['buyPrice'], order['buyOrderSize']))
        else:
            raise RuntimeError("Market buy order returned unexpected response.")

    def sell(self, asset):
        asset['ts'] = asset['data'][-1]['ts']
        orders = asset['orders']
        quoteP = asset['quoteP']
        assetP = asset['assetP']
        balance = asset['balance']
        step = asset['step']
        precision = asset['precision']
        orders[-1]['sell'] = asset['ts']
        value = round(floor(balance / step) * step, assetP)

        trx = self.client.order_market_sell(symbol=asset['symbol'], quantity=value, newOrderRespType='FULL')

        if trx['status'] == 'FILLED':
            quote = float(trx['cummulativeQuoteQty'])
            qty = float(trx['executedQty'])
            commision = round(sum([float(f['commission']) for f in trx['fills']]), quoteP)
            orders[-1]['sellPrice'] = round(quote/qty, precision)
            orders[-1]['sellResult'] = round(quote - commision, quoteP)
            orders[-1]['profit'] = round(orders[-1]['sellResult'] - orders[-1]['buyOrderSize'], quoteP)
            self.quoteBalance = round(self.quoteBalance + orders[-1]['sellResult'], quoteP) 
            asset['balance'] = round(balance - qty, assetP)
            asset['orderLifeTime'] = 0
            print("Sell order: %s, profit: %s" % (orders[-1]['sellPrice'], orders[-1]['profit']))
        else:
            raise RuntimeError("Market sell order returned unexpected response.")

    def buySignal(self, asset):
        data = asset['data']
        if len(data) > 2:
            h1 = data[-2]['macdh']
            h2 = data[-3]['macdh']
            macd1 = data[-2]['macd']
            macd2 = data[-3]['macd']
            a = asset['almostBuySignal']
            if not (h1 is None or h2 is None):
                if not a and (h1 >= 0 and h2 < 0): asset['almostBuySignal'] = True
                if a and (h1 < 0 and h2 >= 0): asset['almostBuySignal'] = False
                return a and (macd1 - macd2 > asset['buySignalStep'])
            else:
                return False
        else:
            return False

    def sellSignal(self, asset):
        data = asset['data']
        if len(data) > 2:
            macd1 = data[-2]['macd']
            macd2 = data[-3]['macd']
            if not (macd1 is None or macd2 is None):
                t = asset['orderLifeTime']
                p = asset['SellSignalInitPeriod']
                s0 = asset['SellSignalInitStep']
                s1 = asset['SellSignalStep']
                return (t < p and macd2 - macd1 > s0) or (t >= p and macd2 - macd1 > s1)
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
