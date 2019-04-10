import random
from abc import ABC
from abc import abstractmethod
from utils.src.python.Logging import has_logger
from behaviour_tree.src.python.lib import BehaveTreeTaskNode

class BehaveTreeControlNode(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
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
            'maybe': BehaveTreeControlNode.maybe,
            'loop-until-success': BehaveTreeControlNode.tickLoopUntilSuccess,
        }[self.kind]

    def configure(self, definition: dict=None):
         super().configure(definition)
         for k in {
             "yield": [ "result" ],
             "maybe": [ "chance", "result" ],
         }.get(self.kind, []):
             setattr(self, k, definition.get(k, None))

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

        return self.children[at]

    def tickAll(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return True

        return self.children[at]

    def maybe(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at == 0:
            r = random.randint(0, self.chance)
            if r != 0:
                return self.result

        if at >= len(self.children):
            return self.result

        return self.children[at]

    def tickFirst(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[1] == True and prev[0] in self.children:
            return True

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return False

        return self.children[at]

    def tickYield(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        if context.has("_yielded"):
            context.delete("_yielded")
            return self.result
        context.set("_yielded", 1)
        return self

    def tickLoop(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            return self

        return self.children[at]

    def tickForever(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        return self

    def tickLoopUntilSuccess(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev=None):
        at = 0

        if prev and prev[1] and prev[0] in self.children:
            return True

        if prev and prev[0] in self.children:
            at = self.children.index(prev[0])
            at += 1

        if at >= len(self.children):
            at = 0

        return self.children[at]
