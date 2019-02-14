from topopt.src.python.Interfaces import ComInterface, SONode, Coord
from typing import List


class DummyGeoOrgNode(SONode):
    def __init__(self, name: str, com: ComInterface, initial_peers: List[str]):
        self.name = name
        self.com = com
        self.peers = initial_peers
        self.h = 0
        self.bottom_left = None
        self.top_right = None
        self.step_left = 0
        self.step_right = 0
        self.step_up = 0
        self.step_down = 0
        self.coord = None
        self.prev = {
            "coord": self.coord,
            "h": self.h,
            "value": 0,
            "peeers": []
        }

    def setHits(self, x: float) -> None:
        self.h = x

    def setRange(self, bottom_left: Coord, top_right: Coord) -> None:
        self.bottom_left = bottom_left
        self.top_right = top_right

    def setStep(self, left: float, right: float, up: float, down: float) -> None:
        self.step_left = left
        self.step_right = right
        self.step_up = up
        self.step_down = down

    def getCoord(self) -> Coord:
        return self.coord

    def getPeers(self) -> List[str]:
        return self.peers

    def getName(self) -> str:
        return self.name

    def value(self):
        return self.h

    def tick(self):
        pass
