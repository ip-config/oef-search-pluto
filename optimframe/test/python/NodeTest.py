import os
import numpy as np
from optimframe.src.python.node.Interfaces import Coord, ComInterface
from optimframe.src.python.node.DummyGeoOrgNode import DummyGeoOrgNode
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse


class Com(ComInterface):
    def getValue(self, node: str) -> float:
        pass

    def getDistance(self, node1: str, node2: str) -> float:
        pass


def get_grid(h: int, w: int, z0, top_left: Coord, bottom_right: Coord):
    x = np.linspace(top_left.x, bottom_right.x, w)
    y = np.linspace(top_left.y, bottom_right.y, h)
    xx, yy = np.meshgrid(x, y)
    land = (xx**2+yy**2+z0)
    return x, y, land


def node(com, bottom_left, top_right, dx, dy, z):
    n = DummyGeoOrgNode("", com, 1./(z[40,40]+0.01), Coord(bottom_left.x+dx*40,top_right.y+dy*40),[])
    n.setRange(bottom_left, top_right)
    n.setStep(-dx, dx, -dy, dy)
    N = 1000
    n.setJumpSize(2)
    n.temp_dec_speed = 2.
    def move():
        nonlocal N, n, z
        for i in range(1,N):
            n.tick(i, N)
            p = n.getCoord()
            xi = int(np.ceil((p.x - bottom_left.x) / dx))
            yi = int(np.ceil((p.y - top_right.y) / dy))
            if xi>=z.shape[0]:
                xi = z.shape[0]-1
            if yi>=z.shape[1]:
                yi = z.shape[1]-1
            n.setHits(1./(z[xi, yi]+0.01))
            yield [i, n.getT(), [xi, yi]]
    return move


def main():
    top_left = Coord(-10, -10)
    bottom_right = Coord(10, 10)
    bottom_left = Coord(-10,10)
    top_right = Coord(10,-10)
    w = 400
    h = 400
    dx = np.abs(top_left.x-bottom_right.x)/float(w)
    dy = np.abs(top_left.y-bottom_right.y)/float(h)
    x, y, z = get_grid(w, h, 50, top_left, bottom_right)

    point = Ellipse((20, 20), 10, 10, 0)
    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
    ax.add_artist(point)
    #point.set_clip_box(ax.bbox)
    #point.set_alpha(np.random.rand())
    #point.set_facecolor(np.random.rand(3))
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 400)
    plt.imshow(z, cmap="hot")
    n = node(Com(), bottom_left, top_right, dx, dy, z)
    plt.colorbar()
    txt = plt.text(200, 430, "Iter: 0, Temp: 1e9")
    for d in n():
        i, T, p = d
        txt.set_text("Iter: %d, Temp: %.3f"%(i, T))
        point.set_center(p)
        fig.canvas.draw()
        plt.pause(0.01)


if __name__ == "__main__":
    main()
