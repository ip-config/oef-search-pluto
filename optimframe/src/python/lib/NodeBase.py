from abc import ABC
from abc import abstractmethod
from optimframe.src.python.openpopgrid import EnglandPopDistro

from optimframe.src.python.lib import popgrab
import random

class NodeBase(ABC):
    def __init__(self):
        self.my_number = NodeBase.counter
        NodeBase.id_to_base[self.my_number] = self
        NodeBase.counter += 1

    def put(self, x, y):
        popgrab.put(self.my_number, x, y)

    @abstractmethod
    def hits(self, hcount):
        pass

    #----------------------------- CLASS METHODS

    counter = 1
    id_to_base = {}

    def setup():
        eng = EnglandPopDistro.EnglandPopDistro()
        eng.load("optimframe/src/data")

        class SetPopVisitor(object):
            def __init__(self):
                pass

            def visit(self,x,y,p):
                popgrab.set_pop(x,y,p)

        eng.visit(SetPopVisitor())

    def run():
        popgrab.run()

        for k,v in NodeBase.id_to_base.items():
            v.hits(popgrab.get(k))
