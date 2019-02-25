from functools import reduce

def prec(v):
    p=0
    while v < 1:
        v*=10
        p+=1
    return p

def genParams(mins, maxs, steps):
        p = [prec(s) for s in steps]
        params = mins.copy()
        while True:
            yield params
            if params == maxs: break
            i = -1
            while True:
                if params[i] < maxs[i]:
                    params[i] = round(params[i] + steps[i], p[i])
                    break
                else:
                    params[i] = mins[i]
                    i -= 1
            