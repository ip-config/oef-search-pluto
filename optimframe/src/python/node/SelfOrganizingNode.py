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
        self.best = {
            "coord": self.coord,
            "value": self.value()
        }
        self.alpha  = 0.0
        self.temp_dec_speed = 1.

    def setHits(self, x: float) -> None:
        self.h = x

    def setRange(self, bottom_left: Coord, top_right: Coord) -> None:
        self.bottom_left = bottom_left
        self.top_right = top_right

    def setStep(self, left: float, right: float, up: float, down: float) -> None:
        self.step_left = Coord(left, 0)
        self.step_right = Coord(right, 0)
        self.step_up = Coord(0, up)
        self.step_down = Coord(0, down)
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
        return 1./(self.h+0.1)

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
        return max(0.001, min(1, 1 - self.temp_dec_speed*fraction))

    def prob(self, v: float, v_new: float, T: float):
        #if v_new < v:
        #    return 0.8
        #else:
            return np.exp(-(v_new-v)/T)

    def getT(self):
        return self.T

    def getMoveProbs(self, max_index, alpha=0.1):
        w = []
        b = self.best["coord"]
        for m in self.move_vector:
            w.append((self.coord.x+m.x-b.x)**2+(self.coord.y+m.y-b.x)**2)
        w = np.array(w)
        w = 1./w
        w = w-np.mean(w)
        mv = np.max(w)
        amin = np.abs(np.min(w))
        if mv<amin:
            mv = amin
        w = np.divide(w, mv)
        w = alpha*w+1./float(max_index)
        w = np.divide(w, np.sum(w))
        return w

    def setAlpha(self, alpha):
        self.alpha = alpha

    def tick(self, iter: int, max_iter: int):
        v = self.value()
        self.T = self.temperature(float(iter)/float(max_iter))
        if self.prob(self.prev["value"], v, self.T) < random.random():
            self.coord = self.prev["coord"]
            self.h = self.prev["h"]
            v = self.value()

        if v < self.best["value"]:
            self.best["value"] = v
            self.best["coord"] = self.coord

        #store current values as prev
        self.prev["value"] = v
        self.prev["coord"] = self.coord
        #make a random move
        long = 1.
        r = random.random()
        if r > 0.9:
            long = 2.
        if r > 0.95:
            long = 3.
        if r > 0.99:
            long = 4
        num_of_moves = 8
        dir_id = np.random.choice(range(num_of_moves), p=self.getMoveProbs(num_of_moves, self.alpha))
        #dir_id = np.random.randint(0, num_of_moves-1)
        move = self.move_vector[dir_id]
        self.coord = self.coord + move*self.jump*long

        if self.coord.x <= self.bottom_left.x:
            self.coord.x = (self.bottom_left+self.step_right).x
        elif self.coord.x > self.top_right.x:
            self.coord.x = (self.top_right+self.step_left).x

        if self.coord.y <= self.top_right.y:
            self.coord.y = (self.top_right+self.step_down).y
        elif self.coord.y>self.bottom_left.y:
            self.coord.y = (self.bottom_left+self.step_up).y
