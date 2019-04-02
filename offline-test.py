from SimpleEMAStrategy import SimpleEMAStrategy
from OfflineTestTrader import OfflineTestTrader

strategy = SimpleEMAStrategy(30, 50)
trader = OfflineTestTrader("./data/2018-1-1-BTCUSDT-5m.csv", strategy)

trader.run()

print("Current balance: %s" % (trader.quoteBalance))