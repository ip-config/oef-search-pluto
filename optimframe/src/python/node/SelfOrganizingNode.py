from optimframe.src.python.node.Interfaces import ComInterface, SONode, Coord
from typing import List
import numpy as np
import random


class DummyGeoOrgNode(SONode):
    def __init__(self, name: str, com: ComInterface, initial_h: float, initial_coord: Coord, initial_peers: List[str]):
        self.name = name
        self.com = com
        self.peers = initial_peers
        self.h = initial_h
        self.bottom_left = None
        self.top_right = None
        self.step_left = None
        self.step_right = None
        self.step_up = None
        self.step_down = None
        self.move_vector = None
        self.coord = initial_coord
        self.prev = {
            "coord": self.coord,
            "h": self.h,
            "value": self.value()
        }
        self.T = 0
        self.jump = 1

    def setHits(self, x: float) -> None:
        self.h = x

    def setRange(self, bottom_left: Coord, top_right: Coord) -> None:
        self.bottom_left = bottom_left
        self.top_right = top_right

    def setStep(self, left: float, right: float, up: float, down: float) -> None:
        self.step_left = Coord(-left, 0)
        self.step_right = Coord(right, 0)
        self.step_up = Coord(0, up)
        self.step_down = Coord(0, -up)
        self.move_vector = self.calculate_move_vector()

    def setJumpSize(self, jump: float):
        self.jump = jump

    def getCoord(self) -> Coord:
        return self.coord

    def getPeers(self) -> List[str]:
        return self.peers

    def getName(self) -> str:
        return self.name

    def value(self) -> float:
        return self.h

    def calculate_move_vector(self):
        diag = lambda v1, v2: (v1+v2).normalized()*(np.sqrt(np.square(v1.len())+np.square(v2.len())))
        return [
            self.step_up,
            diag(self.step_up, self.step_right),
            self.step_right,
            diag(self.step_right, self.step_down),
            self.step_down,
            diag(self.step_down, self.step_left),
            self.step_left,
            diag(self.step_left, self.step_up)
        ]

    def temperature(self, fraction):
        return max(0.001, min(1, 1 - fraction))

    def prob(self, v: float, v_new: float, T: float):
        if v_new > v:
            return 0.9
        else:
            return np.exp(-(v-v_new)/T)

    def getT(self):
        return self.T

    def getMoveProbs(self, max_index):
        w = []
        for m in self.move_vector:
            w.append((self.coord.x+m.x)**2+(self.coord.y+m.y)**2)
        w = np.array(w)
        w = w-np.min(w)
        w = np.divide(w, np.max(w))
        max_index = 7
        w = 0.7*w+1./float(max_index)
        w = np.divide(w, np.sum(w))
        return w

    def tick(self, iter: int, max_iter: int):
        self.T = self.temperature(float(iter)/float(max_iter))
        v = self.value()
        if self.prob(v, self.prev["value"], self.T) >= random.random():
            self.coord = self.prev["coord"]
            self.h = self.prev["h"]
        self.prev["value"] = self.value()
        self.prev["coord"] = self.coord
        long = 1.
        r = random.random()
        if r > 0.9:
            long = 2.
        if r > 0.95:
            long = 4.
        if r > 0.99:
            long = 6
        w = []


        dir_id = random.randint(0, 7)
        move = self.move_vector[dir_id]
        self.coord = self.coord + move*self.jump*long
        if self.coord.x>self.top_right.x:
            self.coord.x = self.top_right.x
        if self.coord.y>self.top_right.y:
            self.coord.y = self.top_right.y
