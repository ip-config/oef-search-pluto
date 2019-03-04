from typing import Callable

from behaviour_tree.src.python.lib import BehaveTree
from behaviour_tree.src.python.lib import BehaveTreeBaseNode
from behaviour_tree.src.python.lib import BehaveTreeTaskNode
from behaviour_tree.src.python.lib import BehaveTreeControlNode

class BehaveTreeLoader(object):
    def __init__(self, *args, **kwargs):
        self.names_to_builders = {
            None: BehaveTreeLoader._noClassname,
        }

    def addBuilder(self, name: str, builder: 'Callable[[BehaveTreeLoader, dict], BehaveTreeBaseNode.BehaveTreeBaseNode]'):
        self.names_to_builders[name] = builder
        return self

    def _noClassname(definition: dict):
        raise ValueError("Can't find a node/type in :" + json.dumps(definition, indent=2))

    def _noBuilder(definition: dict):
        raise ValueError("Can't find builder for node/type in :" + json.dumps(definition, indent=2))

    def build(self, definition: dict):
        func = self.names_to_builders.get(definition.get('node', definition.get('type', None)), BehaveTreeLoader._noBuilder)

        r = func(definition)
        if hasattr(r, 'children'):
            r._buildChildrenFromList(self, definition.get('children', []))
        return r

    def buildAll(self, definitions: list):
        return [ self.build(x) for x in definitions ]
