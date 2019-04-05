from SimpleEMAStrategy import SimpleEMAStrategy
from MACDRSIStrategy import MACDRSIStrategy
from OfflineTestTrader import OfflineTestTrader
from LinearRegressionStrategy import LinearRegressionStrategy

#strategy = LinearRegressionStrategy(3,-1)
strategy = MACDRSIStrategy(14, 30, 70)
trader = OfflineTestTrader("./data/2019-1-1-BTCUSDT-5m.csv", strategy, 1000, 500)

trader.run()

print("Current balance: %s" % (trader.quoteBalance))