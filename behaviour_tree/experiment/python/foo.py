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

class Inc(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        context.setIfAbsent("count", 0)
        context.set("count", context.get("count") + 1)
        return False

    def configure(self, definition: dict=None):
        super().configure(definition=definition)

class Sufficient(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        if context.get("count") > 20:
            print("YES")
            return True

        if context.absent("flag"):
            context.set('flag', 1)
            print("SNOOZE")
            return self

        context.delete('flag')
        print("NO")
        return False

    def configure(self, definition: dict=None):
        super().configure(definition=definition)

TREE1 = """
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

TREE2 = """
{
  "node": "all",
  "name": "nodeALL",
  "children":
  [
    {
      "node": "loop-until-success",
      "name": "loop",
       "children":
       [
         {
           "node": "inc"
         },
         {
           "node": "sufficient"
         }
       ]
    },
    {
      "node": "forever",
      "name": "forever"
    }
  ]
}
"""


def main():
    loader = BehaveTreeLoader.BehaveTreeLoader()

    loader.addBuilder(
        'tick', lambda x: Tick(x)
    ).addBuilder(
        'tocks', lambda x: Tock(x)
    ).addBuilder(
        'inc', lambda x: Inc(x)
    ).addBuilder(
        'sufficient', lambda x: Sufficient(x)
    )

#    tree1 = BehaveTree.BehaveTree(loader.build(json.loads(TREE1)))
#    exe1 = BehaveTreeExecution.BehaveTreeExecution(tree1)
#    for i in range(0, 500):
#        exe1.tick()
#        time.sleep(0.5)

    tree2 = BehaveTree.BehaveTree(loader.build(json.loads(TREE2)))
    exe2 = BehaveTreeExecution.BehaveTreeExecution(tree2)
    for i in range(0, 500):
        exe2.tick()
        time.sleep(0.20)

if __name__ == '__main__':
    main()
