from OfflineTestTrader import OfflineTestTrader
from RSICumMaxStrategy import RSICumMaxStrategy

strategy = RSICumMaxStrategy(k1=33, k2=0.995)
trader = OfflineTestTrader("./data/2019-1-1-BTCUSDT-5m.csv", strategy, 1000, 100)

trader.run()

print("Current balance: %s" % (trader.quoteBalance))