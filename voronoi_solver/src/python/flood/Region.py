class Region(object):

    _NO_DEFAULT_SUPPLIED_EXEMPLAR = object()

    def __init__(self, w, h):
        self.w = w
        self.h = h

    def width(self):
        return self.w

    def height(self):
        return self.h

    def clear(self, blank=0):
        self.store = [
            [ blank ] * self.w for _ in range(0, self.h)
        ]

    def get(self, x, y, defl=_NO_DEFAULT_SUPPLIED_EXEMPLAR):
        if x<0 or x>=self.w or y<0 or y>=self.h:
            if defl != Region._NO_DEFAULT_SUPPLIED_EXEMPLAR:
                return defl
            else:
                raise ValueError((x,y))
        return self.store[y][x]

    def set(self, x, y, value):
        if x<0 or x>=self.w or y<0 or y>=self.h:
            return False
        self.store[y][x]=value
        return True

    def visit(self, rowvisitor, colvisitor):
        return [
            rowvisitor.visit([
                colvisitor.visit(col) for col in row
            ])
            for row in self.store
        ]

    def process(self, itemvisitor):
        for y in range(0, self.h):
            row = self.store[y]
            for x in range(0, self.w):
                row[x] = itemvisitor.visit(row[x])
