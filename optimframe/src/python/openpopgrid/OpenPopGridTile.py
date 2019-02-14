import re

class OpenPopGridTile(object):
    def __init__(self):
        self.cellsize = 1000
        self.w = int(100000 / self.cellsize)
        self.h = int(100000 / self.cellsize)
        self.store = {}

    def print(self):
        for y in range(self.h-1, 0, -1):
            s=""
            for x in range(0, self.w):
                p = self.store.get(
                    (
                        self.x + self.cellsize/2 + x * self.cellsize,
                        self.y + self.cellsize/2 + y * self.cellsize,
                    ), None)
                c = '.'
                if p == None:
                    c = "~"
                else:
                    if p > 1:
                        c = ':'
                    if p > 10:
                        c = '='
                    if p > 30:
                        c = '#'
                s += c
            print(s)

    def save(self, f):
        for y in range(self.h-1, -1, -1):
            row = []
            for x in range(0, self.w):
                p = self.store.get(
                    (
                        self.x + self.cellsize/2 + x * self.cellsize,
                        self.y + self.cellsize/2 + y * self.cellsize,
                    ), 0)
                row.append(str(int(p)))
            f.write(",".join(row) + "\n")

    def load(self, f):
        header = self.loadHeader(f)

        self.x = int(header['x']/100000)*100000
        self.y = int(header['y']/100000)*100000

        self.loadDataLines(f, header)
        print(self.store)

    def loadHeader(self, f):
        header_lines = [
            f.readline(),
            f.readline(),
            f.readline(),
            f.readline(),
            f.readline(),
            f.readline(),
        ]
        return self.loadHeaderValues(header_lines)

    def loadHeaderValues(self, header_lines):
        r = {}
        for inp, pat, att, func in [
            (header_lines[0], r'ncols\s+([-0-9]+)',         'w', lambda x: int(float(x))),
            (header_lines[1], r'nrows\s+([-0-9]+)',         'h', lambda x: int(float(x))),
            (header_lines[2], r'xllcorner\s+([-0-9\.]+)',   'x', lambda x: int(float(x))),
            (header_lines[3], r'yllcorner\s+([-0-9\.]+)',   'y', lambda x: int(float(x))),
            (header_lines[4], r'cellsize\s+([-0-9\.]+)',    'loadcellsize', lambda x: int(float(x))),
            (header_lines[5], r'NODATA_value\s+([-0-9\.]+)','none', lambda x: x),
        ]:
            m = re.search(pat, inp)
            if not m:
                raise Exception("Cannot parse:", inp)
            r[att] = func(m.groups(1)[0])
        return r

    def loadDataLines(self, f, header):

        scale = header['loadcellsize']
        for i in range(header['h']-1, 0, -1):
            if (i % 100) == 0:
                print(i,"...")
            inp = f.readline().strip()
            parts = re.split('\s+', inp)
            if len(parts) != header['w']:
                raise Exception("Short line {}".format(i+1))

            sy =  header['y'] + scale/2 + (i*scale)
            ty = int(sy / self.cellsize)*self.cellsize + self.cellsize/2

            for j,v in enumerate(parts):
                if v == header['none']:
                    continue

                sx =  header['x'] + scale/2 + (j*scale)
                tx = int(sx / self.cellsize)*self.cellsize + self.cellsize/2

                self.store.setdefault((tx,ty), 0)
                self.store[(tx,ty)] += float(v)
