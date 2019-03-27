import sys
import unittest

from dap_api.src.python import DapManager
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python import ProtoHelpers
from utils.src.python.Logging import has_logger

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
            "er-graph": {
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

    def makeAgent(self, x):
        return ( "localhost", x )

    def setupAgents(self):
        g = self.data.getInstance("er-graph").getGraphByTableName("mesh")


        g.addLink(self.makeAgent("james bond"), self.makeAgent("austin danger powers"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("james bond"), self.makeAgent("harry palmer"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("maxwell smart"), self.makeAgent("agent 99"), bidirectional=True, label="show")

        g.addLink(self.makeAgent("maxwell smart"), self.makeAgent("felix leiter"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("james bond"), self.makeAgent("felix leiter"), bidirectional=True, label="show")

        g.addLink(self.makeAgent("maxwell smart"), self.makeAgent("agent 99"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("illya kuryakin"), self.makeAgent("napoleon solo"), bidirectional=True, label="show")
        g.addLink(self.makeAgent("maxwell smart"), self.makeAgent("napoleon solo"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("jason bourne"), self.makeAgent("napoleon solo"), bidirectional=True, label="nation")

        g.addLink(self.makeAgent("john steed"), self.makeAgent("emma peel"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("john steed"), self.makeAgent("emma peel"), bidirectional=True, label="show")
        g.addLink(self.makeAgent("john steed"), self.makeAgent("james bond"), bidirectional=True, label="nation")
        g.addLink(self.makeAgent("emma peel"), self.makeAgent("james bond"), bidirectional=True, label="nation")

    def testDataModelAndAttributeQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()

        qc = qm.constraints.add()

        q1 = qc.and_.expr.add()
        q2 = qc.and_.expr.add()

        q1.constraint.attribute_name = "mesh.origin"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "localhost,austin danger powers"

        q2.constraint.attribute_name = "mesh.weight"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.d = 3.5

        dapQuery = self.data.makeQuery(qm)
        identifierSequence = self.data.execute(dapQuery)
        results = [ x.agent.decode('utf8') for x in identifierSequence.identifiers ]

        assert sorted(results) == [
            'emma peel',
            'felix leiter',
            'harry palmer',
            'james bond',
            'john steed',
            'maxwell smart'
            # agent99 is in the same show as Maxwell, but is 4 steps away from Austin Powers.
        ]

    def XtestDataModelWithLinkLabelsSetQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()

        qc = qm.constraints.add()

        q1 = qc.and_.expr.add()
        q2 = qc.and_.expr.add()
        q3 = qc.and_.expr.add()

        q1.constraint.attribute_name = "mesh.origin"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "localhost,austin danger powers"

        q2.constraint.attribute_name = "mesh.weight"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.d = 3.5

        q3.constraint.attribute_name = "mesh.label"
        q3.constraint.set_.op = 0
        q3.constraint.set_.vals.s.vals.extend([ "nation" ])

        dapQuery = self.data.makeQuery(qm)
        identifierSequence = self.data.execute(dapQuery)
        results = [ x.agent.decode('utf8') for x in identifierSequence.identifiers ]

        # The results now only include BRITISH spies because we're following only the NATION links.
        assert sorted(results) == [
            'emma peel',
            'harry palmer',
            'james bond',
            'john steed',
        ]

    def XtestDataModelWithLinkLabelQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()

        qc = qm.constraints.add()

        q1 = qc.and_.expr.add()
        q2 = qc.and_.expr.add()
        q3 = qc.and_.expr.add()

        q1.constraint.attribute_name = "mesh.origin"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "localhost,austin danger powers"

        q4.constraint.attribute_name = "mesh.origin"
        q4.constraint.relation.op = 0
        q4.constraint.relation.val.s = "austin danger powers"

        q2.constraint.attribute_name = "mesh.weight"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.d = 13.5

        q3.constraint.attribute_name = "mesh.label"
        q3.constraint.relation.op = 0
        q3.constraint.relation.val.s = "nation"

        dapQuery = self.data.makeQuery(qm)
        identifierSequence = self.data.execute(dapQuery)
        results = [ x.agent.decode('utf8') for x in identifierSequence.identifiers ]

        # The results now only include BRITISH spies because we're following only the NATION links.
        assert sorted(results) == [
            'emma peel',
            'harry palmer',
            'james bond',
            'john steed',
        ]

from utils.src.python.Logging import configure as configure_logging
configure_logging()
unittest.main() # run all tests
