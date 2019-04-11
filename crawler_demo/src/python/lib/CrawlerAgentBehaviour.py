import json
import time
import random
import math
import numpy as np
from behaviour_tree.src.python.lib import BehaveTree
from behaviour_tree.src.python.lib import BehaveTreeTaskNode
from behaviour_tree.src.python.lib import BehaveTreeLoader
from behaviour_tree.src.python.lib import BehaveTreeControlNode
from behaviour_tree.src.python.lib import BehaveTreeExecution
from utils.src.python.Logging import has_logger
from enum import Enum


def best_oef_core(nodes):
    distance = 1e16
    result = None
    for node in nodes:
        for res in node.result:
            if res.distance < distance:
                distance = res.distance
                result = res
    return result


class MovementType(Enum):
    CRAWL_ON_NODES = 1
    FOLLOW_PATH = 2


class Reset(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        self.log.update_local_name(context.get("index"))
        self.info("RESET")
        context.setIfAbsent("movement_type", MovementType.CRAWL_ON_NODES)

        node_locations = context.get("locations")
        locs = []
        keys = []
        for i in range(2):
            key = context.randomiser().choice(list(node_locations.keys()))
            loc = (node_locations[key][0] + context.randomiser().randint(-10, 10),
                   node_locations[key][1] + context.randomiser().randint(-10, 10))
            keys.append(key)
            locs.append(loc)
        target_id, source_id = keys
        target_loc, source_loc = locs

        context.set("last-movement", time.time())

        self.warning("NEW TARGET: ", target_loc)
        context.set("target", target_loc)
        context.set('target-x', target_loc[0])
        context.set('target-y', target_loc[1])

        agent = context.get("agent")
        if not context.has('initialised'):
            context.set('initialised', 1)
            agent.connect(target=source_id + "-core")

        context.setIfAbsent("connection", source_id)
        context.setIfAbsent('x', source_loc[0])
        context.setIfAbsent('y', source_loc[1])

        if context.get("movement_type") == MovementType.FOLLOW_PATH:
            context.set('moveto-x', target_loc[0])
            context.set('moveto-y', target_loc[1])

        return True

    def configure(self, definition: dict=None):
        super().configure(definition=definition)


class PickLocation(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        return True

    def configure(self, definition: dict=None):
        super().configure(definition=definition)
        self.range = (
            (
                definition.get('x-lo'), definition.get('y-lo')
            ), (
                definition.get('x-hi'), definition.get('y-hi')
            )
        )


class IsThisANetworkCrawler(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution' = None,
             prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode' = None):
        self.log.update_local_name(context.get("index"))

        if prev and prev[0] in self.children:
            return True

        mode = context.get("movement_type")
        if mode != MovementType.CRAWL_ON_NODES:
            return False

        return self.children[0]

    def configure(self, definition: dict = None):
        super().configure(definition=definition)


class IsThisAPathFollower(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution' = None,
             prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode' = None):
        self.log.update_local_name(context.get("index"))

        if prev and prev[0] in self.children:
            return True

        mode = context.get("movement_type")
        if mode != MovementType.FOLLOW_PATH:
            return False

        return self.children[0]

    def configure(self, definition: dict = None):
        super().configure(definition=definition)


class QueryNodesToMoveTo(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        self.log.update_local_name(context.get("index"))

        agent = context.get("agent")
        target = context.get("target")

        result = best_oef_core(agent.search(target))
        if result is not None:
            self.info(result)
            agent.swap_core(result)
            context.set("connection", result.key.decode("UTF-8").replace("-core", ""))
        else:
            return True

        loc = agent.get_from_core("location")
        if loc is None:
            self.info("Agent at target location!")
            return True
        x = loc.lat
        y = loc.lon

        context.set('moveto-x', x)
        context.set('moveto-y', y)

        dx = x - context.get('x')
        dy = y - context.get('y')

        self.info("NEW INTERMEDIATE GOAL:", context.get('moveto-x'), context.get('moveto-y'), " dx dy", dx, dy)
        dist = math.sqrt(dx*dx + dy*dy)
        if dist != 0.0:
            context.set('delta-x', (dx/dist) * 5 )
            context.set('delta-y', (dy/dist) * 5 )

        return False

    def configure(self, definition: dict=None):
        super().configure(definition=definition)


class AreWeThereYet(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution' = None,
             prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode' = None):
        self.log.update_local_name(context.get("index"))

        dx = context.get("target-x") - context.get("x")
        dy = context.get("target-y") - context.get("y")
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < 10:
            print("AreWeThereYet, returning TRUE")
            return True
        context.set('delta-x', (dx/dist) * 5) #* context.randomiser().randint(2, 5))
        context.set('delta-y', (dy/dist) * 5 ) #* context.randomiser().randint(2, 5))
        return False

    def configure(self, definition: dict = None):
        super().configure(definition=definition)

class QueryNearestNode(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution' = None,
             prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode' = None):
        self.log.update_local_name(context.get("index"))

        agent = context.get("agent")

        x = context.get("x")
        y = context.get("y")

        target_loc = context.get("target")
        result = best_oef_core(agent.search(target_loc))
        if result is not None:
            self.info(result)
            agent.swap_core(result)
            context.set("connection", result.key.decode("UTF-8").replace("-core", ""))

        return False

    def configure(self, definition: dict = None):
        super().configure(definition=definition)


class DoMovement(BehaveTreeTaskNode.BehaveTreeTaskNode):
    @has_logger
    def __init__(self, *args, **kwargs):
        self.one_step = False
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        self.log.update_local_name(context.get("index"))

        # are we at our next location?

        dx = context.get('moveto-x') - context.get('x')
        dy = context.get('moveto-y') - context.get('y')
        if math.sqrt(dx*dx + dy*dy) < 10:
            self.info("AT WAYPOINT/TARGET")
            return False # go back to QueryNodes

        # do some more movement.

        now = time.time()
        prev = context.get("last-movement")

        delta = now - prev;
        context.set("last-movement", now)

        context.set('x', context.get('x') + context.get('delta-x'))
        context.set('y', context.get('y') + context.get('delta-y'))
        if self.one_step == 1:
            return False

        return self

    def configure(self, definition: dict=None):
        super().configure(definition=definition)
        self.one_step = definition.get("one_step", False)


class Snooze(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        context.setIfAbsent('ticks', 0)
        ticks = context.get('ticks')
        if ticks > self.ticks:
            return self.result
        context.set('ticks', ticks + 1)
        return self

    def configure(self, definition: dict=None):
        super().configure(definition=definition)
        self.ticks = definition.get('ticks', 10)
        self.result = definition.get('result', True)


TREE = """
{
  "node": "all",
  "name": "nodeALL",
  "children":
  [
    {
      "node": "Reset",
      "name": "Reset"
    },
    {
      "node": "PickLocation",
      "name": "PickLocation",
      "x-lo": 0,
      "y-lo": 0,
      "x-hi": 699,
      "y-hi": 699
    },
    {
        "node": "first",
        "name": "AgentMovementTypeSelector",
        "children": [
            {
                "node": "IsThisANetworkCrawler",
                "name": "IsThisANetworkCrawler",
                "children": [{
                    "node": "loop-until-success",
                    "name": "network crawler moving loop",
                    "children": [
                        {
                            "node": "QueryNodesToMoveTo",
                            "name": "QueryNodesToMoveTo"
                        },
                        {
                            "node": "yield",
                            "result": 0
                        },
                        {
                            "node": "DoMovement",
                            "name": "DoMovement",
                            "one_step": 0
                        }
                    ]
                }]
            },
            {
                "node": "IsThisAPathFollower",
                "name": "IsThisAPathFollower",
                "children": [{
                    "node": "loop-until-success",
                    "name": "path follower moving loop",
                    "children": [
                        {
                            "node": "AreWeThereYet",
                            "name": "AreWeThereYet2"
                        },
                        {
                            "node": "maybe",
                            "name": "maybe",
                            "chance": 5,
                            "result": 0,
                            "children": [
                                {
                                    "node": "QueryNearestNode",
                                    "name": "QueryNearestNode"
                                }
                            ]
                        },
                        {
                            "node": "yield",
                            "result": 0
                        },
                        {
                            "node": "DoMovement",
                            "name": "DoMovement2",
                            "one_step": 1
                        }
                    ]
                }]
            }
        ]
    }
  ]
}
"""

class CrawlerAgentBehaviour(BehaveTree.BehaveTree):
    def __init__(self):
        loader = BehaveTreeLoader.BehaveTreeLoader()
        loader.addBuilder(
            'Reset', lambda x: Reset(x)
        ).addBuilder(
            'PickLocation', lambda x: PickLocation(x)
        ).addBuilder(
            'AreWeThereYet', lambda x: AreWeThereYet(x)
        ).addBuilder(
            'QueryNodesToMoveTo', lambda x: QueryNodesToMoveTo(x)
        ).addBuilder(
            'QueryNearestNode', lambda x: QueryNearestNode(x)
        ).addBuilder(
            'IsThisANetworkCrawler', lambda x: IsThisANetworkCrawler(x)
        ).addBuilder(
            'IsThisAPathFollower', lambda x: IsThisAPathFollower(x)
        ).addBuilder(
            'DoMovement', lambda x: DoMovement(x)
        ).addBuilder(
            'Snooze', lambda x: Snooze(x)
        )
        super().__init__(loader.build(json.loads(TREE)))
