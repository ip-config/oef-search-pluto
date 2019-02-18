import os
import numpy as np
from optimframe.src.python.node.Interfaces import Coord, ComInterface
from optimframe.src.python.node.SelfOrganizingNode import DummyGeoOrgNode
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse
from optimframe.src.python.openpopgrid import EnglandPopDistro



class Com(ComInterface):
    def getValue(self, node: str) -> float:
        pass

    def getDistance(self, node1: str, node2: str) -> float:
        pass


def get_grid(file, z0=10.):
    eng = EnglandPopDistro.EnglandPopDistro()
    print("LOADING...")
    eng.load(file)

    top_left = Coord(0, 700)
    bottom_right = Coord(700, 0)
    w = eng.w
    h = eng.h

    data = np.zeros((w, h), dtype=np.float)
    for i in range(h):
        for j in range(w):
            data[i,j] = eng.get(i,j)+z0

    return data, w, h, top_left, bottom_right


def node(com, bottom_left, top_right, dx, dy, z):
    i0 = 500
    j0 = 450
    n = DummyGeoOrgNode("", com, z[i0,j0], bottom_left+Coord(dx*i0,dy*j0),[])
    n.setRange(bottom_left, top_right)
    n.setStep(dx, dx, dy, dy)
    N = 10000
    n.setJumpSize(2)
    def move():
        nonlocal N, n, z
        for i in range(1,N):
            n.tick(i, N)
            p = n.getCoord()
            xi = int((p.x - bottom_left.x) / dx)
            yi = int((p.y - bottom_left.y) / dy)
            n.setHits(z[xi, yi])
            yield [i, n.getT(), [xi, yi]]
    return move


def main():
    land, w, h, top_left, bottom_right = get_grid("optimframe/src/data")
    dx = np.abs(top_left.x - bottom_right.x) / float(w)
    dy = np.abs(top_left.y - bottom_right.y) / float(h)

    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    plt.imshow(np.log(land), cmap="hot")
    plt.colorbar()

    point = Ellipse((100, 100), 10, 10, 0)
    point.set_facecolor('white')
    ax.add_artist(point)
    bottom_left = Coord(top_left.x, bottom_right.y)
    top_right = Coord(bottom_right.x, top_left.y)
    n = node(Com(), bottom_left, top_right, dx, dy, land)
    txt = plt.text(350, 730, "Iter: 0, Temp: 1e9")
    for d in n():
        i, T, p = d
        txt.set_text("Iter: %d, Temp: %.3f"%(i, T))
        point.set_center(p)
        fig.canvas.draw()
        plt.pause(0.01)


if __name__ == "__main__":
    main()
