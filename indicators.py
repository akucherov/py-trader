class Indicators():

    def sma(self, data, window):
        if len(data) < window:
            raise ValueError("data is too short")
        return sum(data[-window:]) / float(window)

    def ema(self, value, window, prev_ema):
        c = 2.0 / (window + 1)
        return c*(value - prev_ema) + prev_ema

    def wma(self, data, window):
        if len(data) < window:
            raise ValueError("data is too short")
        i = 1 
        s = sum(range(1,window+1))
        wma = 0
        for value in data[-window:]:
            wma += (i/s)*value
            i+=1
        return wma

    def emas(self, data, window):
        l = len(data)
        if l < window:
            raise ValueError("data is too short")
        e = [self.sma(data[0:window], window)]
        for value in data[window:]:
            e.append(self.ema(value, window, e[-1]))
        return e