from behaviour_tree.src.python.lib import BehaveTree
from behaviour_tree.src.python.lib import BehaveTreeBaseNode

class BehaveTreeExecution(object):

    instances = 0

    def __init__(self, tree: BehaveTree=None, randomiser=None):
        self.tree = tree
        self.context = {}
        self.stack = [ tree.root ]
        self._randomiser = randomiser or random.Random()
        self.name = "BehaveTreeExecution-{}".format(BehaveTreeExecution.instances)
        BehaveTreeExecution.instances += 1

    def tick(self):
        prev=None
        throttle = 0
        while throttle < 25:
            throttle += 1
            foo = self.stack.pop()
            r = foo._execute(context=self, prev=prev)

#            pp = prev
#            if pp != None:
#                if pp[1]:
#                    pp = "({},{})".format(pp[0].printable(), pp[1])
#                else:
#                    pp = "({},{})".format(pp[0], pp[1])
#            rp = r
#            if hasattr(rp, "printable"):
#                rp = rp.printable()
#            print(self.name, "TICK: cycle=", throttle, "   step=", foo.printable(), "prev=", pp, " RESULT => ", rp)


            prev=(foo, r)

            if r == True:
                #print("(done, go round)")
                continue
            elif r == False or r == None:
                #print("(done, go round)")
                continue
            elif r == foo:
                self.stack.append(r)
                #print("Need idle..")
                break;
            else:
                self.stack.append(foo)
                self.stack.append(r)
                #print("Working..")

    def printable(self):
        r = ""
        for k, v in self.context.items():
            vv = "??"
            try:
                vv = str(v)
            except:
                pass
            r += "{}={}\n".format(k, v)
        return r

    def randomiser(self):
        return self._randomiser

    def has(self, something):
        return something in self.context

    def absent(self, something):
        return something not in self.context

    def set(self, something, value):
        self.context[something] = value

    def get(self, something):
        return self.context.get(something, None)

    def setIfAbsent(self, something, value):
        if something not in self.context:
            self.context[something] = value
        return self

    def delete(self, something):
        del self.context[something]
        return self

    def pushTask(self, task):
        self.stack.append(task)
