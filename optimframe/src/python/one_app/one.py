import random

from optimframe.src.python.lib import NodeBase

class TestNode(NodeBase.NodeBase):
    def __init__(self, name, x, y):
        super().__init__()
        self.name = name
        self.put(x,y)

    def hits(self, hitcount):
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

if __name__ == "__main__":
    main()
