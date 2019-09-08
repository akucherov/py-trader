import pandas as pd
from OfflineTestTrader import OfflineTestTrader
from RSISLStrategy import RSISLStrategy

strategy = RSISLStrategy(k1=28, k2=8, k3=5, k4=0.997, size=288)
d1 = pd.Timestamp('2019-01-1 11:00:00')
d2 = pd.Timestamp('2019-05-1 00:00:00')
trader = OfflineTestTrader("./data/2019-1-1-BTCUSDT-5m.csv", strategy, 1000, 100, before=d1, after=d2)

trader.run()

print("Current balance: %s" % (trader.quoteBalance))