from myunit import Vector
from random import randint

def slice2list(s: slice, length, /) -> list:
    '''
    step = s.step or 1
    if step > 0:
        return list(range(s.start or 0, s.stop or length, step))
    else:
        return list(range(s.start or -1, s.stop or -length - 1, step))'''
    return list(range(length)[s])
    
def randsilce():
    start = randint(-7, 8)
    if start == 8: start = None
    step = randint(-3, 3)
    if step == 0: step = None
    stop = randint(-7, 8)
    if stop == 8: stop = None
    return slice(start, stop, step)

v = Vector(range(13))
u = list(range(13))
#print(v, v[::-1], v[::-2], v[::-3], None > 0, sep='\n')
for _ in range(10):
    s = randsilce()
    index = slice2list(s, len(u))
    print(_, s, u[s], v[s], index, v[index], sep='\n')