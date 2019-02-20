import os
import numpy as np
from optimframe.src.python.node.Interfaces import Coord, ComInterface
from optimframe.src.python.node.DummyGeoOrgNode import DummyGeoOrgNode
from optimframe.src.python.node.QGeoOrgNode import QGeoOrgNode
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse
from optimframe.src.python.openpopgrid import EnglandPopDistro
from optimframe.src.python.lib import NodeBase


class TestNode(NodeBase.NodeBase):
    def __init__(self, node: DummyGeoOrgNode):
        super().__init__()
        self.name = node.name
        self.node = node

    def hits(self, hitcount):
        self.node.setHits(hitcount)

    def update_coords(self):
        coord = self.node.getCoord()
        self.put(int(coord.x+0.5), int(coord.y+0.5))



class Com(ComInterface):
    def getValue(self, node: str) -> float:
        pass

    def getDistance(self, node1: str, node2: str) -> float:
        pass


def get_grid(file, z0=10.):
    eng = EnglandPopDistro.EnglandPopDistro()
    print("LOADING...")
    eng.load(file)

    top_left = Coord(0, 0)
    bottom_right = Coord(700, 700)
    w = eng.w
    h = eng.h

    data = np.zeros((w, h), dtype=np.float)
    for i in range(h):
        for j in range(w):
            data[j,i] = eng.get(i,j)+z0

    data = np.flipud(data)

    return data, w, h, top_left, bottom_right


def setup_nodes(num_of_nodes, ax, com, bottom_left, top_right, dx, dy, z, N=100000):
    nodes = []
    points = []
    for i in range(num_of_nodes):
        i0 = np.random.randint(200, 600)
        j0 = np.random.randint(100, 600)
        coord = Coord(bottom_left.x+dx * i0, top_right.y+dy * j0)
        n = DummyGeoOrgNode(str(i), com, z[i0, j0], coord, [])
        n.setRange(bottom_left, top_right)
        n.setStep(-dx, dx, dy, -dy)
        n.setJumpSize(4)
        n.setAlpha(0.1)
        #n.setEpsilon(0.1)
        #n.setStateSize(700,700)
        #n.setQParams(0.01, 0.9)
        n.temp_dec_speed = 4.
        node_wrapper = TestNode(n)
        nodes.append(node_wrapper)
        point = Ellipse((coord.x, coord.y), 10, 10, 0)
        point.set_facecolor('blue')
        ax.add_artist(point)
        points.append(point)
    regions = np.ones((700,700), dtype=np.int)
    def move():
        nonlocal nodes, points, regions
        for i in range(1, N):
            NodeBase.NodeBase.run()
            rewards = ""
            for n in range(len(nodes)):
                nodes[n].node.tick(i, N)
                nodes[n].update_coords()
                p = nodes[n].node.getCoord()
                xi = int(np.ceil((p.x - bottom_left.x) / dx))
                yi = int(np.ceil((p.y - top_right.y) / dy))
                T  = nodes[n].node.getT()
                points[n].set_center([xi, yi])
                rewards += "%d: %.2f; "%(n, nodes[n].node.value())
            NodeBase.NodeBase.set_regions(regions)
            #print(rewards)
            print(regions)
            yield [i, T]
    return move


def main():
    NodeBase.NodeBase.setup()
    land, w, h, top_left, bottom_right = get_grid("optimframe/src/data", -10)
    dx = np.abs(top_left.x - bottom_right.x) / float(w)
    dy = np.abs(top_left.y - bottom_right.y) / float(h)
    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    plt.imshow(np.log(land+20), cmap="hot")
    plt.colorbar()

    bottom_left = Coord(top_left.x, bottom_right.y)
    top_right = Coord(bottom_right.x, top_left.y)

    n = setup_nodes(20, ax, Com(), bottom_left, top_right, dx, dy, land)
    txt = plt.text(350, 730, "Iter: 0, Temp: 1e9")
    for d in n():
        i, T = d
        txt.set_text("Iter: %d, Temp: %.3f"%(i, T))
        fig.canvas.draw()
        plt.pause(0.01)


if __name__ == "__main__":
    main()
