import random

from optimframe.src.python.lib import NodeBase
from optimframe.src.python.lib import popgrab

class TestNode(NodeBase.NodeBase):
    def __init__(self, name, x, y):
        super().__init__()
        self.name = name
        self.put(x,y)

    def hits(self, hitcount):
        print(self.name, hitcount)
        self.hitcount = hitcount


def main():

    NodeBase.NodeBase.setup()

    NAMES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    nodes = [
        TestNode(n, random.randint(0, 699), random.randint(0, 699))
        for n in NAMES
    ]

    NodeBase.NodeBase.run()

    t = sum([
        n.hitcount
        for n in nodes
    ])
    print(t)


    temp = popgrab.PopGrab(100, 100)
    for a in "ABCDE":
        temp.put(ord(a), random.randint(0, 99), random.randint(0, 99))
    temp.run()
    for y in range(0,100):
        s=""
        for x in range(0,100):
            s += chr(temp.read_reg(x,y))
        print(s)


if __name__ == "__main__":
    main()
