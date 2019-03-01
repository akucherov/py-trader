from functools import reduce
from math import floor

def prec(v):
    p=0
    while v < 1:
        v*=10
        p+=1
    return p

def genParams(mins, maxs, steps):
        p = [prec(s) for s in steps]
        l = - len(mins)
        i = -1
        params = mins.copy()
        while True:
            if i < l: break
            yield params
            while True:
                if params[i] < maxs[i]:
                    params[i] = round(params[i] + steps[i], p[i])
                    i = -1
                    break
                else:
                    params[i] = mins[i]
                    i -= 1
                    if i < l: break
            
def periods(l,n):
    p = floor(l/n)
    return [(i)*p for i in range(1,n)]