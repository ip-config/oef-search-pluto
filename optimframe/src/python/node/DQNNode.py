from optimframe.src.python.node.Interfaces import Coord
from optimframe.src.python.node.DQN import DQN
from typing import List
import numpy as np
import random


class StateAdaptor:
    def __init__(self, bottom_left: Coord, top_right: Coord, orig_dim: np.array, state_dim: np.array):
        self.dx = np.abs(top_right.x-bottom_left.x)/float(orig_dim[0])
        self.dy = np.abs(top_right.y-bottom_left.y)/float(orig_dim[1])
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.dim_rescale = np.divide(orig_dim, state_dim.astype(np.float))
        self.dim_rescale_inv = np.divide(state_dim, orig_dim.astype(np.float))
        self.state_dim = state_dim

    def state_to_coord(self, state):
        pos = np.array(np.unravel_index(np.argmax(state[:, :, 0]), dims=self.state_dim))
        transformed_pos = np.multiply(pos, self.dim_rescale)
        x = transformed_pos[0]*self.dx+self.bottom_left.x
        y = transformed_pos[1]*self.dy+self.top_right.y
        return Coord(x,y)

    def coord_to_state(self, coord: Coord):
        i0 = (coord.x-self.bottom_left.x)/self.dx
        j0 = (coord.y - self.top_right.y) / self.dy
        i = i0*self.dim_rescale_inv[0]
        j = j0*self.dim_rescale_inv[1]
        return int(i+0.5), int(j+0.5)

    def near_edge(self, coord, jump):
        return coord.x<=jump or coord.x>=(self.top_right.x-jump) or coord.y<=jump or coord.y>=(self.bottom_left.y-jump)


class DQNGeoOrgNode:
    def __init__(self, name: str, stateAdaptor: StateAdaptor):
        self.name = name
        self.state_adaptor = stateAdaptor
        self.state = None
        self._h = 0
        self._h_prev = 0
        self.update_step = True
        self._channels = 3
        self.agent = DQN(32, 256, (stateAdaptor.state_dim[0], stateAdaptor.state_dim[1], self._channels, 5), name)
        self.current_action = None
        self.prev_state = None
        self.jump = 1
        self._cached_coord = None

    def setHits(self, x: float) -> None:
        self._h_prev = self._h
        self._h = x

    def getCoord(self) -> Coord:
        if self._cached_coord is not None:
            return self._cached_coord
        self._cached_coord = self.state_adaptor.state_to_coord(self.state)
        return self._cached_coord

    def reward(self) -> float:
        #if self.state_adaptor.near_edge(self.getCoord(), self.jump):
        #    return -1.
        diff = self._h - self._h_prev
        r = 0
        if diff > 0:
            r = 1
        elif diff < 0:
            r = -1
        return r

    def setJump(self, jump):
        self.jump = jump

    def initState(self, initial_position: Coord):
        self.state = np.zeros((self.state_adaptor.state_dim[0], self.state_adaptor.state_dim[1], self._channels))
        tipi, tipj = self.state_adaptor.coord_to_state(initial_position)
        self.state[tipi, tipj, 0] = 1

    def setOthersState(self, everybody):
        self.state[:, :, 1] = (everybody[:, :, 0]-self.state[:, :, 0])

    def setLastChannel(self, data):
        self.state[:, :, 2] = data/np.max(data)

    def getLoss(self):
        return self.agent.getLoss()

    def update_state(self, state, action):
        self._cached_coord = None
        w = state.shape[0]
        h = state.shape[1]
        pos = np.unravel_index(np.argmax(state[:, :, 0]), dims=(w, h))
        pos = np.array(pos)
        state[pos[0], pos[1], 0] = 0.
        new_pos = np.array(pos)
        if action == 0:
            new_pos[0] = min(pos[0]+self.jump, w-self.jump)
        elif action == 1:
            new_pos[1] = min(pos[1]+self.jump, h-self.jump)
        elif action == 2:
            new_pos[0] = max(pos[0]-self.jump, self.jump)
        elif action == 3:
            new_pos[1] = max(pos[1]-self.jump, self.jump)
        else:
            print("Unknown action: {}".format(action))
        state[new_pos[0], new_pos[1], 0] = 1.

    def tick(self):
        if self.update_step:
            self.update_step = False
            self.prev_state = np.copy(self.state)
            self.current_action = self.agent.predict_action(self.prev_state)
            self.update_state(self.state, self.current_action)
        else:
            self.update_step = True
            self.agent.remember(self.prev_state, self.current_action, self.reward(), self.state)

    def train(self, episode):
        self.agent.replay(episode)
        if episode % 5 == 0:
            self.agent.trainTarget()
