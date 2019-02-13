import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_api.experimental.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2

class UpdateTest(unittest.TestCase):
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

    def testUpdate(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        update = self._createUpdate()
        self.dap1.update(update.update[0])

    def testUpdateBadType(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        update =self._createUpdate()
        update.update[0].value.type = 3
        update.update[0].value.i = 12345

        with self.assertRaises(Exception) as context:
            self.dap1.update(update.update[0])

    def testNoTableUpdate(self):
        update = self._createUpdate()

        with self.assertRaises(Exception) as context:
            self.dap2.update(update.update[0])

