from abc import ABC, abstractmethod
from typing import List


class Coord:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class ComInterface(ABC):
    @abstractmethod
    def getValue(self, node: str) -> float:
        pass

    @abstractmethod
    def getDistance(self, node1: str, node2: str) -> float:
        pass


class SONode(ABC):
    @abstractmethod
    def __init__(self, name: str, com: ComInterface, initial_peers: List[str]):
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
    def getCoord(self) -> Coord:
        pass

    @abstractmethod
    def getPeers(self) -> List[str]:
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def tick(self):
        pass
