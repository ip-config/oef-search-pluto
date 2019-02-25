import numpy as np
import os, sys
from optimframe.src.python.node.Interfaces import Coord, ComInterface
from optimframe.src.python.node.DQNNode import DQNGeoOrgNode, StateAdaptor
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from optimframe.src.python.openpopgrid import EnglandPopDistro
from optimframe.src.python.lib import NodeBase


class TestNode:
    def __init__(self, node: DQNGeoOrgNode, g1, g2, c1: Coord, c2: Coord):
        super().__init__()
        self.name = node.name
        self.n = node
        self.g1 = g1
        self.g2 = g2
        self.c1 = c1
        self.c2 = c2
        self.current = None

    def hits(self, hitcount):
        self.n.setHits(np.log(hitcount+100))

    def update_coords(self):
        coord = self.n.getCoord()
        self.current = coord

    def tick(self):
        self.n.tick()
        self.update_coords()

    def run(self):
        if self.current is None:
            return
        i = int(self.current.x+0.5)
        j = int(self.current.y+0.5)
        #dist = np.sqrt((self.c1.x-self.current.x)**2+(self.c1.y-self.current.y)**2)
        self.hits(self.g1[i, j])


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

    x = np.linspace(top_left.x, bottom_right.x, w)
    y = np.linspace(top_left.y, bottom_right.y, h)
    xx, yy = np.meshgrid(x, y)
    g1 = 1e8/((xx-200) ** 2 + (yy-200) ** 2)
    g2 = 1e8/((xx-400) ** 2 + (yy-400) ** 2)
    land = g1+g2

    return land, w, h, top_left, bottom_right, g1, g2


def node_initializer(bottom_left, top_right, dx, dy, num_of_rand_nodes = 0):
    f = open("toby_loader/data/csv/centres-ordered-by-population.csv", "r")
    cities = [line.split(',') for line in f.readlines()]

    def init(nodes):
        rnd_i = 0
        citi_i = 0
        for i in range(len(nodes)):
            if rnd_i < num_of_rand_nodes:
                rnd_i += 1
                i0 = np.random.randint(50, 650)
                j0 = np.random.randint(50, 650)
            else:
                i0 = int(cities[citi_i][2])
                j0 = int(cities[citi_i][1])
                citi_i += 1
            coord = Coord(bottom_left.x + dx * i0, top_right.y + dy * j0)
            nodes[i].n.initState(coord)
    return init


def getVisPoints(ax, nodes):
    points = []
    for node in nodes:
        coord = node.n.getCoord()
        point = Ellipse((coord.x, coord.y), 10, 10, 0)
        point.set_facecolor('blue')
        ax.add_artist(point)
        points.append(point)
    return points


def updateNodeStateChannel1(nodes):
    res = np.zeros_like(nodes[0].n.state)
    for node in nodes:
        res = np.add(res, node.n.state)
    for node in nodes:
        node.n.setOthersState(res)


def updateLastChannel(nodes, land):
    for node in nodes:
        node.n.setLastChannel(land)


def setup_nodes(num_of_nodes, ax, bottom_left, top_right, dx, dy, episodes, N, land, g1, g2):
    node_init = node_initializer(bottom_left, top_right, dx, dy, 2)

    nodes = []
    stateAdaptor = StateAdaptor(bottom_left, top_right, np.array([700, 700]), np.array([700, 700]))
    for i in range(num_of_nodes):
        n = DQNGeoOrgNode(str(i), stateAdaptor)
        n.setJump(6)
        node_wrapper = TestNode(n, land, g2, Coord(200, 200), Coord(400,400))
        nodes.append(node_wrapper)

    node_init(nodes)
    points = getVisPoints(ax, nodes)
    updateNodeStateChannel1(nodes)
    updateLastChannel(nodes, land)

    def move():
        nonlocal nodes, points
        for e in range(episodes):
            node_init(nodes)
            for i in range(N):
                rewards = ""
                losses = ""
                for ni in range(len(nodes)):
                    nodes[ni].run()
                    rewards += "e: %d, i: %d, n: %d: %.2f (%.2f), " % (e, i, ni, nodes[ni].n.reward(), nodes[ni].n._h)
                    losses += "e: {}, i: {}, n: {}: {};".format(e, i, ni, str(nodes[ni].n.getLoss()))
                    nodes[ni].tick()
                    p = nodes[ni].n.getCoord()
                    points[ni].set_center([p.x, p.y])
                updateNodeStateChannel1(nodes)
                if i % 2 == 1:
                    print("Rewards: {}".format(rewards))
                    print("Losses: {}".format(losses))
                if e%2 == 0 and i % 2 == 0:
                    yield [e, i]
            for n in nodes:
                n.n.train()

    return move


def main():
    print(os.getcwd())
    path = os.getcwd()
    anim_dir = path + "/anim6"
    if not os.path.exists(anim_dir):
        os.mkdir(anim_dir)
    #NodeBase.NodeBase.setup()
    land, w, h, top_left, bottom_right, g1, g2 = get_grid("optimframe/src/data", -10)
    dx = np.abs(top_left.x - bottom_right.x) / float(w)
    dy = np.abs(top_left.y - bottom_right.y) / float(h)
    fig, ax = plt.subplots(subplot_kw={'aspect': 'equal'})
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    plt.imshow(np.log(land+20), cmap="hot")
    plt.colorbar()
    bottom_left = Coord(top_left.x, bottom_right.y)
    top_right = Coord(bottom_right.x, top_left.y)

    n = setup_nodes(2, ax, bottom_left, top_right, dx, dy, 200, 256, land, g1, g2)
    txt = plt.text(350, 730, "Iter: 0")
    for d in n():
        txt.set_text("Episode: %d, Iter: %d" % (d[0], d[1]))
        fig.canvas.draw()
        episode_dir = anim_dir + "/{}".format(d[0])
        if not os.path.exists(episode_dir):
            os.mkdir(episode_dir)
        plt.savefig("{}/{}.png".format(episode_dir, d[1]))


if __name__ == "__main__":
    main()
