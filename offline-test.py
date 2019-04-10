from OfflineTestTrader import OfflineTestTrader
from SupportLinesStrategy import SupportLinesStrategy

strategy = SupportLinesStrategy(n=36, k1=1, k3=1, size=144)
trader = OfflineTestTrader("./data/2019-1-1-BTCUSDT-5m.csv", strategy, 1000, 100)

trader.run()

print("Current balance: %s" % (trader.quoteBalance))