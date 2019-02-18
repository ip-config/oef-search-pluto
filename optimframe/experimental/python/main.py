import random

from voronoi_solver.src.python.flood import Region
from voronoi_solver.src.python.flood import RegionFiller
from voronoi_solver.src.python.flood import colours

class RowVisitor(object):
    def __init__(self):
        pass

    def visit(self, x):
        print(''.join(x))

class ColVisitor(object):
    def __init__(self):
        pass

    def visit(self, x):
        if x == 0:
            return '.'
        if isinstance(x, tuple):
            return colours.COLOUR_CONTROL_CODES[{
                'start': 'on-yellow',
                'border': 'blue',
                '': '',
            }[x[2]]] + x[0] + colours.COLOUR_CONTROL_CODES['off']
        return x

def main():
    r = Region.Region(500,300)

    r.clear()
    r.visit(RowVisitor(), ColVisitor())

    filler = RegionFiller.RegionFiller(r)

    for s in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789':
        filler.addStart(s, random.randint(0, r.width()-1), random.randint(0, r.height()-1), s)

    filler.fill()

    r.visit(RowVisitor(), ColVisitor())

if __name__ == "__main__":
    main()
