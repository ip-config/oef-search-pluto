from abc import ABC, abstractmethod
from typing import List
import numpy as np


class Coord:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def len(self) -> float:
        return np.sqrt(np.square(self.x)+np.square(self.y))

    def __mul__(self, other: float):
        return Coord(self.x*other, self.y*other)

    def normalized(self):
        r = self.len()
        return Coord(self.x/r, self.y/r)


class ComInterface(ABC):
    @abstractmethod
    def getValue(self, node: str) -> float:
        pass

    @abstractmethod
    def getDistance(self, node1: str, node2: str) -> float:
        pass


class SONode(ABC):
    def __init__(self, name: str, com: ComInterface, initial_h: float, initial_coord: Coord, initial_peers: List[str]):
        pass

    @abstractmethod
    def setHits(self, x: float) -> None:
        pass

    @abstractmethod
    def setRange(self, bottom_left: Coord, top_right: Coord) -> None:
        pass

    @abstractmethod
    def setStep(self, left: float, right: float, up: float, down: float) -> None:
        pass

    @abstractmethod
    def setJumpSize(self, jump: float) -> None:
        pass

    @abstractmethod
    def getCoord(self) -> Coord:
        pass

    @abstractmethod
    def getPeers(self) -> List[str]:
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def tick(self, iter: int, max_iter: int):
        pass
