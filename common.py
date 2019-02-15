def prec(v):
    p=0
    while v < 1:
        v*=10
        p+=1
    return p