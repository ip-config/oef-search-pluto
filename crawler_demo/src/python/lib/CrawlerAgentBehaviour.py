import json
import time
import random
import math

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

        target = (200, 200) #"Leeds"
        source = "Southampton"
        agent_id = "car-1"

        connection_factory = context.get("connection_factory")
        agent = context.get("agent")

        if agent is None:
            agent = FakeAgent.FakeAgent(connection_factory=connection_factory, id=agent_id)
        else:
            agent.disconnect(None)

        agent.connect(target=source + "-core")

        loc = agent.get_from_core("location")

        context.setIfAbsent('moveto-x', loc.lon)
        context.setIfAbsent('moveto-y', loc.lat)
        context.setIfAbsent('target-x', target[0])
        context.setIfAbsent('target-y', target[1])

        context.setIfAbsent('x', loc.lon)
        context.setIfAbsent('y', loc.lat)

        context.setIfAbsent("agent", agent)
        context.setIfAbsent("target", target)

        return True

    def configure(self, definition: dict=None):
        super().configure(definition=definition)


class PickLocation(BehaveTreeTaskNode.BehaveTreeTaskNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, context: 'BehaveTreeExecution.BehaveTreeExecution'=None, prev: 'BehaveTreeBaseNode.BehaveTreeBaseNode'=None):

        # x = context.get('x')
        # y = context.get('y')
        #
        # print("PickLocation from {},{}".format(x,y))
        #
        # targetx = random.randint(self.range[0][0], self.range[1][0])
        # targety = random.randint(self.range[0][1], self.range[1][1])
        #
        #
        # dx = targetx - x
        # dy = targety - y
        #
        # waypoints = []
        #
        # dist = math.sqrt(dx*dx+dy*dy)
        # for waypoint in range(1, int(dist/100)):
        #     wayx = dx/dist * 100 * waypoint
        #     wayy = dy/dist * 100 * waypoint
        #
        #     wayx += random.randint(-10, 10)
        #     wayy += random.randint(-10, 10)
        #
        #     waypoints.append( (wayx, wayy) )
        # waypoints.append( (targetx, targety) )
        #
        # context.set('waypoints', waypoints)
        #
        # print("NEW TARGET {},{}".format(
        #     targetx, targety
        #     ))
        # print("WAYPOINTS {}".format(
        #     waypoints
        #     ))
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

        waypoints = context.get('waypoints')
        if waypoints == None or waypoints == []:
            print("GOAL!!!!")
            return True

        #waypoint = waypoints.pop(0)
        #context.set('waypoints', waypoints)

        agent = context.get("agent")
        target = context.get("target")

        print(target)
        print(agent)
        query = build_query(target)

        result = best_oef_core(agent.search(query))
        agent.swap_core(result)
        loc = agent.get_from_core("location")

        dx = loc.lon - context.get('x')
        dy = loc.lat - context.get('y')

        context.set('moveto-x', loc.lon)
        context.set('moveto-y', loc.lat)

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
        context.setIfAbsent("count", 0)

        if context.get("count") > random.randint(0, self.duration):
            context.delete("count")
            return True

        return self

    def configure(self, definition: dict=None):
        super().configure(definition=definition)
        self.duration=definition.get('duration')

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
      "node": "loop-until-success",
      "name": "moving loop",
      "children":
      [
        {
          "node": "QueryNodes",
          "name": "QueryNodes"
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
        )
        super().__init__(loader.build(json.loads(TREE)))
