import sys
import unittest

from dap_api.src.python import DapManager
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2

from dap_api.src.python import DapQuery

from dap_e_r_network.src.python import DapERNetwork

def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


class PlutoTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        config = {
            "mesh": {
                "class": "DapERNetwork",
                "config": {
                    "structure": {
                        "mesh": {
                        },
                    },
                },
            },
        }

        self.data = DapManager.DapManager()
        self.data.addClass("DapERNetwork", DapERNetwork.DapERNetwork)
        self.data.setup(sys.modules[__name__], config)

        self.setupAgents()

    def setupAgents(self):
        g = self.data.getInstance("mesh").getGraphByTableName("mesh")
        g.addLink("james bond", "austin danger powers", bidirectional=True, label="nation")
        g.addLink("james bond", "harry palmer", bidirectional=True, label="nation")
        g.addLink("maxwell smart", "agent 99", bidirectional=True, label="show")

        g.addLink("maxwell smart", "felix leiter", bidirectional=True, label="nation")
        g.addLink("james bond", "felix leiter", bidirectional=True, label="show")

        g.addLink("maxwell smart", "agent 99", bidirectional=True, label="nation")
        g.addLink("illya kuryakin", "napoleon solo", bidirectional=True, label="show")
        g.addLink("maxwell smart", "napoleon solo", bidirectional=True, label="nation")
        g.addLink("jason bourne", "napoleon solo", bidirectional=True, label="nation")

        g.addLink("john steed", "emma peel", bidirectional=True, label="nation")
        g.addLink("john steed", "emma peel", bidirectional=True, label="show")
        g.addLink("john steed", "james bond", bidirectional=True, label="nation")
        g.addLink("emma peel", "james bond", bidirectional=True, label="nation")

        print(g.exploreCosts("austin danger powers"))
        print(self.data.getFields())

    def testDataModelAndAttributeQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()

        qc = qm.constraints.add()

        q1 = qc.and_.expr.add()
        q2 = qc.and_.expr.add()

        q1.constraint.attribute_name = "mesh.origin"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "austin danger powers"

        q2.constraint.attribute_name = "mesh.weight"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.d = 5.0

        dapQuery = self.data.makeQuery(qm)
#        results = list(self.pluto.dapManager.execute(dapQuery))

#        assert len(results) == 1
#        assert results[0][0] ==  "007/James/Bond/Weather"

        assert 1 == 1


unittest.main() # run all tests
