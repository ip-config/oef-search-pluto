from abc import ABC
from abc import abstractmethod

from behaviour_tree.src.python.lib import BehaveTreeTaskNode

class BehaveTreeControlNode(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, kind=None, definition: dict=None, *args, **kwargs):
        self.kind = kind
        super().__init__(definition, args, kwargs)
        self.tickfunc = {
            None: None,
            'all': BehaveTreeControlNode.tickAll,
            'each': BehaveTreeControlNode.tickEach,
            'first': BehaveTreeControlNode.tickFirst,
            'loop': BehaveTreeControlNode.tickLoop,
            'forever': BehaveTreeControlNode.tickForever,
            'yield': BehaveTreeControlNode.tickYield,
            'loop-until-success': BehaveTreeControlNode.tickLoopUntilSuccess,
        }[self.kind]

    def configure(self, definition: dict=None):
         super().configure(definition)
         for k in {
             "yield": [ "result" ],
         }.get(self.kind, []):
             self.k = definition.get(k, None)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        #print("SELF=", self, " kind=", self.kind)
        #print("PREV=", prev)
        #print("CHILDREN=", self.children)
        return self.tickfunc(self, context=context, prev=prev)

    def tickEach(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[1] == False:
            return False

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return True

        context.pushTask(self)
        context.pushTask(self.children[at])
        return True

    def tickAll(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return True

        context.pushTask(self)
        context.pushTask(self.children[at])
        return True

    def tickFirst(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[1] == True:
            return True

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return False

        context.pushTask(self)
        context.pushTask(self.children[at])
        return True

    def tickYield(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        if prev == None:
            return True if self.result == None else self.result
        return self

    def tickLoop(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return self

        context.pushTask(self)
        context.pushTask(self.children[at])
        return True

    def tickForever(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        return self

    def tickLoopUntilSuccess(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[1] and prev[0] in self.children:
            print("CHILD SUCCESS")
            return True

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            at = 0

        context.pushTask(self)
        context.pushTask(self.children[at])
        return True
