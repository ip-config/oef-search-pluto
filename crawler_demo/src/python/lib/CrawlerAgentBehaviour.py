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
from fake_oef.src.python.lib import FakeAgent
from crawler_demo.src.python.lib.SearchNetwork import SearchNetwork, ConnectionFactory
from api.src.proto import query_pb2, response_pb2


def build_query(target=(200, 200)):
    q = query_pb2.Query()
    q.model.description = "weather data"
    q.ttl = 1
    q.directed_search.target.geo.lat = target[0]
    q.directed_search.target.geo.lon = target[1]
    return q


def best_oef_core(nodes):
    distance = 1e16
    result = None
    for node in nodes:
        for res in node.result:
            if res.distance < distance:
                distance = res.distance
                result = res
    return result


class Reset(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        print("RESET")

        context.setIfAbsent('x', np.random.randint(50, 650))
        context.setIfAbsent('y', np.random.randint(50, 650))

        context.set('target-x', context.get('x'))
        context.set('target-y', context.get('y'))

        return True

    def configure(self, definition: dict=None):
        super().configure(definition=definition)


class PickLocation(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):

        target = (np.random.randint(50, 650), np.random.randint(50, 650)) #"Leeds"
        print("NEW TARGET: ", target)
        context.set("target", target)
        context.set('target-x', target[0])
        context.set('target-y', target[1])

        connection_factory = context.get("connection_factory")

        if not context.has("agent"):
            source = "Southampton"
            agent_id = "car-"+str(np.random.randint(1, 100))
            agent = FakeAgent.FakeAgent(connection_factory=connection_factory, id=agent_id)
            agent.connect(target=source + "-core")
            context.set("connection", source)
            context.set("agent", agent)
            loc = agent.get_from_core("location")
            context.setIfAbsent('x', loc.lat)
            context.setIfAbsent('y', loc.lon)

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

class QueryNodes(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):

        #waypoints = context.get('waypoints')
        #if waypoints == None or waypoints == []:
        #    print("GOAL!!!!")
        #    return True

        #waypoint = waypoints.pop(0)
        #context.set('waypoints', waypoints)


        print("tick")
        agent = context.get("agent")
        target = context.get("target")

        print(target)
        print(agent)
        query = build_query(target)

        result = best_oef_core(agent.search(query))
        if result is not None:
            print(result)
            agent.swap_core(result)
            context.set("connection", result.key.decode("UTF-8").replace("-core", ""))
        else:
            return True
        loc = agent.get_from_core("location")

        if loc is None:
            print(result)
            print(agent.connections)
            print("NOOO")
            return True

        dx = loc.lat - context.get('x')
        dy = loc.lon - context.get('y')

        context.set('moveto-x', loc.lat)
        context.set('moveto-y', loc.lon)

        print("NEW INTERMEDIATE GOAL:", context.get('moveto-x') , context.get('moveto-y') )
        dist = math.sqrt(dx*dx + dy*dy)
        if dist != 0.0:
            context.set('delta-x', (dx/dist) * 5 )
            context.set('delta-y', (dy/dist) * 5 )

        return False

    def configure(self, definition: dict=None):
        super().configure(definition=definition)


class DoMovement(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):

        # are we at our next location?

        dx = context.get('moveto-x') - context.get('x')
        dy = context.get('moveto-y') - context.get('y')

        if math.sqrt(dx*dx + dy*dy) < 20:
            print("AT WAYPOINT/TARGET")
            return False # go back to QueryNodes

        # do some more movement.

        context.set('x', context.get('x') + context.get('delta-x'))
        context.set('y', context.get('y') + context.get('delta-y'))
        return self

    def configure(self, definition: dict=None):
        super().configure(definition=definition)


class Snooze(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):
        print("SNOOZE")

        context.setIfAbsent('ticks', 0)
        ticks = context.get('ticks')
        print("TICKS=", ticks, self.ticks)

        if self.ticks < ticks:
            return self.result

        context.set('ticks', ticks + 1)
        print("TICKS=", ticks, self.ticks)

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
      "node": "Snooze",
      "name": "Snooze",
      "ticks": 10,
      "result": 0
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
      "node": "loop-until-success",
      "name": "moving loop",
      "children":
      [
        {
          "node": "QueryNodes",
          "name": "QueryNodes"
        },
        {
          "node": "yield",
          "result": 0
        },
        {
          "node": "DoMovement",
          "name": "DoMovement"
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
            'QueryNodes', lambda x: QueryNodes(x)
        ).addBuilder(
            'DoMovement', lambda x: DoMovement(x)
        ).addBuilder(
            'Snooze', lambda x: Snooze(x)
        )
        super().__init__(loader.build(json.loads(TREE)))
