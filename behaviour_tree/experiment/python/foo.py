#!/usr/bin/env python3

import json
import time

from behaviour_tree.src.python.lib import BehaveTree
from behaviour_tree.src.python.lib import BehaveTreeTaskNode
from behaviour_tree.src.python.lib import BehaveTreeLoader
from behaviour_tree.src.python.lib import BehaveTreeControlNode
from behaviour_tree.src.python.lib import BehaveTreeExecution

class Tick(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        print("Tick")
        return True

    def configure(self, definition: dict=None):
        super().configure(definition=definition)

class Tock(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        context.setIfAbsent("tocks", 0)

        context.set("tocks", context.get("tocks") + 1)
        if context.get("tocks") <= self.count:
            print("Tock ",context.get("tocks"), " of ", self.count)

        if context.get("tocks") >= self.count:
            context.delete("tocks")
            return True
        return self

    def configure(self, definition: dict=None):
        super().configure(definition=definition)
        self.count = definition.get("tocks", 1)

TREE = """
{
  "node": "all",
  "name": "nodeALL",
  "children":
  [
    {
      "node": "tick",
      "name": "nodeA"
    },
    {
      "node": "tocks",
      "tocks": 2,
      "name": "nodeB"
    },
    {
      "node": "tick",
      "name": "nodeC"
    },
    {
      "node": "tocks",
      "tocks": 4,
      "name": "nodeD"
    }
  ]
}
"""

def main():
    loader = BehaveTreeLoader.BehaveTreeLoader()

    loader.addBuilder(
        'all', lambda x: BehaveTreeControlNode.BehaveTreeControlNode('all',x)
    ).addBuilder(
        'each', lambda x: BehaveTreeControlNode.BehaveTreeControlNode('each',x)
    ).addBuilder(
        'first', lambda x: BehaveTreeControlNode.BehaveTreeControlNode('first',x)
    ).addBuilder(
        'loop', lambda x: BehaveTreeControlNode.BehaveTreeControlNode('loop',x)
    ).addBuilder(
        'tick', lambda x: Tick(x)
    ).addBuilder(
        'tocks', lambda x: Tock(x)
    )

    tree = BehaveTree.BehaveTree(loader.build(json.loads(TREE)))

    exe1 = BehaveTreeExecution.BehaveTreeExecution(tree)
    exe2 = BehaveTreeExecution.BehaveTreeExecution(tree)

    for i in range(0, 500):
        exe1.tick()
        time.sleep(0.99)

if __name__ == '__main__':
    main()
