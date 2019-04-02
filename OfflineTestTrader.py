import pandas as pd
from datetime import datetime
from math import floor
from collections import defaultdict

class OfflineTestTrader:

    def __init__(self, csv, strategy, balance=1000, orderSize=100, step=0.000001, assetPrecision=8, quotePrecision=8):
        self.df = pd.read_csv(csv)
        self.strategy = strategy
        self.status = 0
        self.ts = 0
        self.assetBalance = 0
        self.orders = []

        self.quoteBalance = balance
        self.orderSize = orderSize
        self.step = step
        self.assetP = assetPrecision
        self.quoteP = quotePrecision

    def run(self):
        for _, row in self.df.iterrows():
            self.strategy.capture(row['Open time'], row['Open'], row['Close'], row['High'], row['Low'], row['Volume'], row['Number of trades'])
            
            if self.status == 0 and self.quoteBalance >= self.orderSize and self.strategy.buySignal():
                self.status = 1
                self.buy(row['Open time'], row['Close'])
                self.ts = row['Open time']

            if self.status == 1 and self.ts != row['Open time'] and self.strategy.sellSignal():
                self.status = 0
                self.sell(row['Open time'], row['Close'])
                self.ts = row['Open time']

    def buy(self, ts, price, log=True):
        order = defaultdict(lambda:None)
        order['buy'] = int(ts/1000)

        value = round(floor((self.orderSize / price) / self.step) * self.step, self.assetP)
        quote = round(price * value, self.quoteP)
        commission = round(value / 1000, self.assetP)

        order['buyPrice'] = round(quote/value, self.strategy.precision)
        order['buyVolume'] = round(value - commission, self.assetP)
        order['buyOrderSize'] = quote
        self.quoteBalance = round(self.quoteBalance - quote, self.quoteP)
        self.assetBalance = round(self.assetBalance + order['buyVolume'], self.assetP)
        self.orders.append(order)
        if log:print("%s: buy order: %s, order size: %s" % (datetime.fromtimestamp(order['buy']), order['buyPrice'], order['buyOrderSize']))

    def sell(self, ts, price, log=True):
        self.orders[-1]['sell'] = int(ts/1000)
        value = round(floor(self.assetBalance / self.step) * self.step, self.assetP)

        quote = round(price * value, self.quoteP)
        commission = round(quote / 1000, self.quoteP)

        self.orders[-1]['sellPrice'] = round(quote/value, self.strategy.precision)
        self.orders[-1]['sellResult'] = round(quote - commission, self.quoteP)
        self.orders[-1]['profit'] = round(self.orders[-1]['sellResult'] - self.orders[-1]['buyOrderSize'], self.quoteP)
        self.quoteBalance = round(self.quoteBalance + self.orders[-1]['sellResult'], self.quoteP) 
        self.assetBalance = round(self.assetBalance - value, self.assetP)
        if log:print("%s: sell order: %s, profit: %s" % (datetime.fromtimestamp(self.orders[-1]['sell']), self.orders[-1]['sellPrice'], self.orders[-1]['profit']))

            