from behaviour_tree.src.python.lib import BehaveTree
from behaviour_tree.src.python.lib import BehaveTreeBaseNode

class BehaveTreeExecution(object):
    def __init__(self, tree: BehaveTree):
        self.tree = tree
        self.context = {}
        self.stack = [ tree.root ]

    def tick(self):
        #print("START---------------",  [ x.name for x in self.stack])
        prev=None
        while True:
            foo = self.stack.pop()
            #print("STACK---------------", [ x.name for x in self.stack])
            #print("CURRENT-------------", foo.name)
            #print("PREV----------------", prev, prev[0].name if prev else "")
            r = foo._execute(context=self, prev=prev)
            #print("STACK-2-------------", [ x.name for x in self.stack])
            prev=(foo, r)
            #print("RES:", r)

            if r == True:
                #print("(done, go round)")
                continue
            elif r == False:
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
