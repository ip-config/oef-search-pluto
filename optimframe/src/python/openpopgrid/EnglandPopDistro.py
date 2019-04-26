import os

class EnglandPopDistro(object):
    def __init__(self):
        self.cellsize = 1000
        self.loadGrid = [
    #       [ "NA", "NB", "NC", "ND", "__", "__", "__" ],
    #       [ "NF", "NG", "NH", "NJ", "NK", "__", "__" ],
    #       [ "NL", "NM", "NN", "NO", "__", "__", "__" ],
            [ "NQ", "NR", "NS", "NT", "NU", "__", "__" ],
            [ "NV", "NW", "NX", "NY", "NZ", "__", "__" ],

            [ "SA", "SB", "SC", "SD", "SE", "TA", "__" ],
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
        self.unloaded = []

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
                    else:
                        self.unloaded.append(tilename)

    def getTileRange(self, tilename):
        for jj in [ 0,1,2,3,4,5,6]:
            for ii in [ 0,1,2,3,4,5,6]:
                if self.loadGrid[jj][ii] == tilename:
                    return (
                        (ii*100,ii*100+99,),
                        (jj*100,jj*100+99,),
                    )

    def savePNG(self):
        import numpy as np
        import math
        from PIL import Image, ImageOps
        m = float(self.max())
        array = np.empty([700, 700, 3])

        class RenderVisitor(object):
            def __init__(self, array):
                self.array = array
            def visit(self, x, y, p, **kwargs):
                n = float(p)
                n /= m

                if p == 0.0:
                    r = 0.6
                    g = 0.8
                    b = 1.0
                else:
                    r = 0.75 - 0.75 * math.sqrt(math.sqrt(n))
                    g = r*1.1
                    b = r

                self.array[y,x,0] = r*255
                self.array[y,x,1] = g*255
                self.array[y,x,2] = b*255

        self.visit(RenderVisitor(array))
        img = Image.fromarray(array.astype('uint8'), 'RGB')
        img.save('pop.png')

    def saveNew(self, path):
        for jj in [ 0,1,2,3,4,5,6]:
            for ii in [ 0,1,2,3,4,5,6]:
                tilename = self.loadGrid[jj][ii]

                if tilename != "__":
                    fn = tilename + ".pop-dist.km.txt"
                    path = os.path.join("optimframe/src/data", fn)
                    if os.path.exists(path):
                        continue
                    with open(path, "w") as fh:
                        self.saveFile(fh, ii*100, jj*100)

    def saveFile(self, fh, xp, yp):
        for y in range(0, 100):
            row = yp + y;
            line = ','.join(
                [
                    self.store[row][xp + x]
                    for x
                    in range(0, 100)
                ]
            )
            fh.writeline(line)

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

    def put(self, x, y, c):
        try:
            self.store[y][x]=c
        except Exception as x:
            print(x,y)
            raise x

    def max(self):
        return max([ max(row) for row in self.store ])

    def visit(self, visitor):
        for y in range(0, self.h):
            for x in range(0, self.w):
                p = self.store[y][x]
                c = EnglandPopDistro.popToChar(p)
                visitor.visit(x,y, p, character=c)
            if hasattr(visitor, 'rowcomplete'):
                visitor.rowcomplete()

    def popToChar(p):
        c = ' '
        if p > 1:
            c = '.'
        if p > 10:
            c = ':'
        if p > 25:
            c = '='
        if p > 50:
            c = '#'
        return c

    def print(self):
        for y in range(0, self.h):
            s=""
            for x in range(0, self.w):
                p = self.store[y][x]
                s += EnglandPopDistro.popToChar(p)
            print(s)
