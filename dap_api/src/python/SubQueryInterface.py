from abc import abstractmethod
from typing import Sequence

class SubQueryInterface(object):
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, agents: Sequence[str]=None):
        pass
