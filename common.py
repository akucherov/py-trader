from functools import reduce

def prec(v):
    p=0
    while v < 1:
        v*=10
        p+=1
    return p

def genParams(size, min, max, step):
        p = prec(step)
        params = [float(min)]*size
        while True:
            yield params
            if reduce(lambda a, v: a and (v == max), params, True): break
            i = -1
            while True:
                if params[i] < max:
                    params[i] = round(params[i] + step, p)
                    break
                else:
                    params[i] = float(min)
                    i -= 1
            