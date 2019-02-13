import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_api.experimental.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2

current_module = sys.modules[__name__]

import sys, inspect
def getClasses(module):
    r = {}
    for name, obj in inspect.getmembers(module):
        if inspect.ismodule(obj):
            for name, obj in inspect.getmembers(obj):
                if inspect.isclass(obj):
                    r[name] = obj
        if inspect.isclass(obj):
            r[name] = obj
    return r

class QueryTest(unittest.TestCase):
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
        self.dapManager.setDataModelEmbedder("", "", "")
        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

        self.dap1 = self.dapManager.getInstance("dap1")
        self.dap2 = self.dapManager.getInstance("dap2")

    def tearDown(self):
        """Call after every test case."""
        pass

    def _createUpdate(self):
        update = dap_update_pb2.DapUpdate()
        newvalue = update.update.add()
        newvalue.tablename = "wibbles"
        newvalue.fieldname = "wibble"
        newvalue.value.type = 2
        newvalue.value.s = "moo"
        newvalue.key = "007/James/Bond".encode("utf-8")
        return update

    def _setupAgents(self):
        for core_key, wibble_value in [
            ("007/James/Bond",   "apple"),
            ("White/Spy",        "banana"),
            ("Black/Spy",        "carrot"),
            ("86/Maxwell/Smart", "carrot"),
        ]:
            update = self._createUpdate()
            update.update[0].key = core_key.encode("utf-8")
            update.update[0].value.s = wibble_value
            self.dap1.update(update.update[0])

        for core_key in [
            "007/James/Bond/apple",
            "White/Spy/banana",
            "Black/Spy/carrot",
            "86/Maxwell/Smart/carrot",
        ]:
            update = self._createUpdate()
            update.update[0].tablename = "wobbles"
            update.update[0].fieldname = "wobble"
            update.update[0].key = core_key.encode("utf-8")
            self.dap2.update(update.update[0])


    def testQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self._setupAgents()

        qm = query_pb2.Query.Model()
        q = qm.constraints.add()

        q.constraint.attribute_name = "wibble"
        q.constraint.relation.op = 0
        q.constraint.relation.val.s = "carrot"

        dapQuery = self.dapManager.makeQuery(qm)
        results = list(self.dapManager.execute(dapQuery))

        assert len(results) == 2

    def testQueryOr(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self._setupAgents()

        qm = query_pb2.Query.Model()
        qOr = qm.constraints.add()

        q1 = qOr.or_.expr.add()
        q2 = qOr.or_.expr.add()

        q1.constraint.attribute_name = "wibble"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "carrot"

        q2.constraint.attribute_name = "wibble"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.s = "apple"


        dapQuery = self.dapManager.makeQuery(qm)
        results = list(self.dapManager.execute(dapQuery))
        assert len(results) == 3
