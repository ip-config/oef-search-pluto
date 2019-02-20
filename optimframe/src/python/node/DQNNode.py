from optimframe.src.python.node.Interfaces import ComInterface, SONode, Coord
from typing import List
import numpy as np
import random


class QGeoOrgNode(SONode):
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
        self.hprev = 0
        self.prev = {
            "coord": self.coord,
            "h": self.h,
            "value": self.value()
        }
        self.jump = 1
        self.best = {
            "coord": self.coord,
            "value": self.value()
        }
        self.alpha  = 0.0
        self.temp_dec_speed = 1.
        self.prevState = 0
        self.move = True
        self.current_action = 0

    def setHits(self, x: float) -> None:
        self.hprev = self.h
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
        return self.h-self.hprev

    def setStateSize(self, w, h, nw=28, nh=28):
        self.width = w
        self.height = h
        self.QTable = np.zeros((nw*nh, len(self.move_vector)))
        self.state_to_coord = {}
        dx = w/nw
        dy=h/nh
        for i in range(nw):
            for j in range(nh):
                self.state_to_coord[i+nw*j] = Coord(i*dx, j*dy)
        self.state = (np.random.randint(0,nw-1), np.random.randint(0, nh-1))
        self.state_to_idx = lambda ij: ij[0]+nw*ij[1]
        self.nw = nw
        self.nh = nh

    def setEpsilon(self, eps=0.1):
        self.epsilion = eps

    def calculate_move_vector(self):
        diag = lambda v1, v2: (v1+v2).normalized()*(np.sqrt(np.square(v1.len())+np.square(v2.len())))
        return [
            self.step_up,
            #diag(self.step_up, self.step_right),
            self.step_right,
            #diag(self.step_right, self.step_down),
            self.step_down,
            #diag(self.step_down, self.step_left),
            self.step_left,
            #diag(self.step_left, self.step_up)
        ]

    def get_random_action(self):
        return random.randint(0, len(self.move_vector)-1)

    def coords_to_state(self, coord):
        i = int(coord.x)
        j = int(coord.y)
        return i+self.width*j

    def setQParams(self, alpha, gamma):
        self.alpha = alpha
        self.gamma = gamma

    def update_state(self, action):
        if action==0:
            self.state = (self.state[0]+1, self.state[1])
        elif action==1:
            self.state = (self.state[0], self.state[1]+1)
        elif action==2:
            self.state = (self.state[0]-1, self.state[1])
        elif action==3:
            self.state= (self.state[0], self.state[1]-1)
        if self.state[0]<0:
            self.state = (0, self.state[1])
        elif self.state[0]>=self.nw:
            self.state = (self.nw-1, self.state[1])
        if self.state[1]<0:
            self.state = (self.state[0],0)
        elif self.state[1]>=self.nh:
            self.state = (self.state[0], self.nh-1)

    def reset(self):
        self.h = 0
        self.state = (np.random.randint(0, self.nw-1), np.random.randint(0, self.nh-1))
        self.coord = self.state_to_coord[self.state_to_idx(self.state)]

    def tick(self, iter: int, max_iter: int):
        if self.move:
            if random.random() < self.epsilion or np.sum(self.QTable[self.state_to_idx(self.state),:])==0:
                action = self.get_random_action()
            else:
                action = np.argmax(self.QTable[self.state_to_idx(self.state), :])
                print(self.state, self.QTable[self.state_to_idx(self.state),:])
            self.prevState = self.state
            self.current_action = action
            #self.coord = self.coord+self.move_vector[action]*self.jump
            self.update_state(action)
            self.coord = self.state_to_coord[self.state_to_idx(self.state)]
            self.move = False
        else:
            self.move = True
            old_q = self.QTable[self.state_to_idx(self.prevState), self.current_action]
            next_max = np.max(self.QTable[self.state_to_idx(self.state), :])
            self.QTable[self.state_to_idx(self.prevState), self.current_action] = (1-self.alpha)*old_q+self.alpha*(self.value()+self.gamma*next_max)