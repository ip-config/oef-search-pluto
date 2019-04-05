import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_2d_geo.src.python import DapGeo
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger

current_module = sys.modules[__name__]

import sys, inspect

class DapGeoTest(unittest.TestCase):

    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Call before every test case."""

        self.dapManager = DapManager.DapManager()

        dapManagerConfig = {
            "geo": {
                "class": "DapGeo",
                "config": {
                    "structure": {
                        "location": {
                        },
                    },
                },
            },
        }
        self.dapManager.setDataModelEmbedder("", "", "")
        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

    def _setupAgents(self):
        for agent, loc in [
            ("007/James/Bond",   (51.477,-0.461)), # LHR
            ("White/Spy",        (53.354,-2.275)), # MANCHESTER
            ("Black/Spy",        (50.734,-3.414)), #EXETER
            ("86/Maxwell/Smart", (40.640,-73.779)), # JFK
        ]:
            update = dap_update_pb2.DapUpdate()
            update.update.add()
            update.update[0].tablename = "location"
            update.update[0].fieldname = "location.update"
            update.update[0].key.core = b'localhost'
            update.update[0].key.agent = agent.encode("utf-8")
            update.update[0].value.l.lat = loc[0]
            update.update[0].value.l.lon = loc[1]
            update.update[0].value.type = 9
            self.dapManager.update(update)
            #self.dapManager.getInstance('geo').place(  ( b'localhost', agent.encode("utf-8")), loc )

    def testProx(self):

        self._setupAgents()

        qm = query_pb2.Query.Model()
        qAnd = qm.constraints.add()

        q1 = qAnd.and_.expr.add()
        q2 = qAnd.and_.expr.add()

        q1.constraint.attribute_name = "location.radius"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.i = 150 * 1000

        q2.constraint.attribute_name = "location.location"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.l.lat = 52.454  # BHX
        q2.constraint.relation.val.l.lon = -1.748


        dapQuery = self.dapManager.makeQuery(qm)
        output = self.dapManager.execute(dapQuery)
        results = list(output.identifiers)
        print("RESULTS:", results)
        assert len(results) == 2
        assert output.HasField("status") == False
