import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_api.src.python import DapQueryRepn
from dap_api.experimental.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2

class DapManagerTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.dapManager = DapManager.DapManager()

        dapManagerConfig = {
            "dap1": {
                "class": "InMemoryDap",
                "config": {
                    "structure": {
                        "wibbles": {
                            "wibble": "string"
                        },
                    },
                },
            },
            "dap2": {
                "class": "InMemoryDap",
                "config": {
                    "structure": {
                        "wobbles": {
                            "wobble": "string"
                        },
                    },
                },
            },
        }
        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)
        self.dap1 = self.dapManager.getInstance("dap1")
        self.dap2 = self.dapManager.getInstance("dap2")

    def _createUpdate(self, agent_name):
        update = dap_update_pb2.DapUpdate()
        newvalue = update.update.add()
        newvalue.tablename = "wibbles"
        newvalue.fieldname = "wibble"
        newvalue.value.type = 2
        newvalue.value.s = "moo"
        newvalue.key.agent = agent_name.encode("utf-8")
        newvalue.key.core = "localhost".encode("utf-8")
        return update

    def _setupAgents(self):
        for agent_name, wibble_value in [
            ("007/James/Bond",   "apple"),
            ("White/Spy",        "banana"),
            ("Black/Spy",        "carrot"),
            ("86/Maxwell/Smart", "carrot"),
        ]:
            update = self._createUpdate(agent_name)
            update.update[0].value.s = wibble_value
            self.dap1.update(update.update[0])

        for agent_name, wobble_value in [
            ("007/James/Bond",   "apple2"),
            ("White/Spy",        "banana2"),
            ("Black/Spy",        "carrot22"),
            ("86/Maxwell/Smart", "carrot2"),
        ]:
            update = self._createUpdate(agent_name)
            update.update[0].tablename = "wobbles"
            update.update[0].fieldname = "wobble"
            update.update[0].value.s = wobble_value
            self.dap2.update(update.update[0])


    def testQueryWriter(self):
        self._setupAgents()

        qm = query_pb2.Query.Model()
        qAnd = qm.constraints.add()
        q1 = qAnd.and_.expr.add()
        q2 = qAnd.and_.expr.add()

        q1.constraint.attribute_name = "wibble"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "carrot"

        q2.constraint.attribute_name = "wobble"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.s = "carrot2"

        dapQuery = self.dapManager.makeQuery(qm)
        results = list(self.dapManager.execute(dapQuery).identifiers)
        assert len(results) == 1
        assert results[0].agent == b'86/Maxwell/Smart'
