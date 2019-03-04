from abc import ABC
from abc import abstractmethod


from behaviour_tree.src.python.lib import BehaveTreeControlNode

class BehaveTree(object):
    def __init__(self, root, *args, **kwargs):
        self.root = BehaveTreeControlNode.BehaveTreeControlNode('loop', definition = { "name": "ROOT" } )
        self.root.children = [ root ]
