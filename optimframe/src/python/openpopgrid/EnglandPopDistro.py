import os

class EnglandPopDistro(object):
    def __init__(self):
        self.cellsize = 1000
        self.loadGrid = [
            [ "__", "__", "__", "NT", "NU", "__", "__" ],
            [ "__", "__", "NX", "NY", "NZ", "__", "__" ],
            [ "__", "__", "__", "SD", "SE", "TA", "__" ],
            [ "__", "__", "SH", "SJ", "SK", "TF", "TG" ],
            [ "__", "SM", "SN", "SO", "SP", "TL", "TM" ],
            [ "__", "SR", "SS", "ST", "SU", "TQ", "TR" ],
            [ "SV", "SW", "SX", "SY", "SZ", "TV", "__" ],
        ]
        self.w = 700
        self.h = 700

        self.store = [
            [ 0 ] * 700 for _ in range(0,700)
        ]

    def load(self, path):
        for jj in [ 0,1,2,3,4,5,6]:
            for ii in [ 0,1,2,3,4,5,6]:
                tilename = self.loadGrid[jj][ii]

                if tilename != "__":
                    fn = tilename + ".pop-dist.km.txt"
                    path = os.path.join("optimframe/src/data", fn)
                    if os.path.exists(path):
                        with open(path, "r") as fh:
                            self.loadFile(fh, ii*100, jj*100)

    def loadFile(self, fh, xp, yp):
        for y in range(0, 100):
            row = yp + y;
            line = fh.readline().strip()
            if len(line)==0:
                continue
            inp = [ int(p) for p in line.split(',') ]
            for x,p in enumerate(inp):
                col = xp + x
                self.store[row][col] = p

    def get(self, x, y):
        return self.store[y][x]

    def max(self):
        return max([ max(row) for row in self.store ])

    def visit(self, visitor):
        for y in range(0, self.h):
            for x in range(0, self.w):
                p = self.store[y][x]
                visitor.visit(x,y,p)

    def print(self):
        for y in range(0, self.h):
            s=""
            for x in range(0, self.w):
                p = self.store[y][x]
                c = ' '
                if p > 1:
                    c = '.'
                if p > 10:
                    c = ':'
                if p > 25:
                    c = '='
                if p > 50:
                    c = '#'
                s += c
            print(s)
