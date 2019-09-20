_neighbor26 = [(x, y, z) for x in range(-1,2) for y in range(-1,2) for z in range(-1,2) if abs(x) + abs(y) + abs(z) > 0]
def neighbor26():
    return _neighbor26

_neighbor6 = [(x, y, z) for x in range(-1,2) for y in range(-1,2) for z in range(-1,2) if abs(x) + abs(y) + abs(z) == 1]
def neighbor6():
    return _neighbor6

