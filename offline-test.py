from SimpleEMAStrategy import SimpleEMAStrategy
from MACDRSIStrategy import MACDRSIStrategy
from OfflineTestTrader import OfflineTestTrader

strategy = MACDRSIStrategy(14,30,70,0.5)
trader = OfflineTestTrader("./data/2018-1-1-BTCUSDT-5m.csv", strategy)

trader.run()

print("Current balance: %s" % (trader.quoteBalance))