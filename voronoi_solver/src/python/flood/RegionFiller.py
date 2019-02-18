import collections

class RegionFiller(object):
    def __init__(self, target):
        self.target = target
        self.starts = {}

    def addStart(self, name, x, y, colour=None):
        self.starts[name]=(x,y,colour if colour != None else name)

    def delStart(self, name):
        self.starts.pop(name)

    def highlightstarts(self):
        for x,y,c in self.starts.values():
            self.target.set(x,y,' ')

    class ItemVisitor(object):
        def __init__(self):
            pass

        def visit(self, x):
            return x[0]

    def fill(self, empty=0):
        pending = collections.deque()

        for x,y,c in self.starts.values():
            pending.append( (x, y, c, 0) )

        w = self.target.width()
        h = self.target.height()

        paint = 0
        while len(pending) > 0:
            x,y,c,gen = pending.pop()
            there = self.target.get(x,y)
            if there == empty or there[1]>gen:
                paint+=1
                if (paint % 10000)==0:
                    print(paint, "/", w*h, len(pending))
                g = gen + 1
                border = False
                for i,j in [
                    (x+1,y+1,),
                    (x+1,y,),
                    (x+1,y-1,),
                    (x,y+1,),
                    (x,y-1,),
                    (x-1,y+1,),
                    (x-1,y,),
                    (x-1,y-1,),
                ]:
                    if i<0 or j<0 or i>=w or j>=h:
                        continue
                    t = self.target.get(i,j)
                    if t == empty:
                        pending.appendleft( (i,j,c,g) )
                    elif t[1]>gen:
                        pending.appendleft( (i,j,c,g) )
                    elif t[0] != c:
                        border = True
                self.target.set(x,y,(c, gen, 'border' if border else ''))

        for x,y,c in self.starts.values():
            self.target.set(x,y,(c, 0, 'start'))

        #self.target.process(RegionFiller.ItemVisitor())
