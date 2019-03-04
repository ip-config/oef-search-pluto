from abc import ABC
from abc import abstractmethod

from behaviour_tree.src.python.lib import BehaveTreeBaseNode

class BehaveTreeTaskNode(BehaveTreeBaseNode.BehaveTreeBaseNode):
    def __init__(self, definition: dict=None, *args, **kwargs):
        super().__init__(definition, args, kwargs)
