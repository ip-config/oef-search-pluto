import unittest

from dap_api.src.python import DapInterface
from dap_api.experimental.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2

class UpdateTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.dap1 = InMemoryDap.InMemoryDap("dap1", { "wibbles": { "wibble": "string" } } );
        self.dap2 = InMemoryDap.InMemoryDap("dap2", { "wobbles": { "wobble": "string" } } );

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
        newvalue.key.agent_name = "007/James/Bond"
        newvalue.key.core_uri.append("localhost:10000")
        return update

    def testUpdate(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        update = self._createUpdate()
        self.dap1.update(update)

    def testUpdateBadType(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        update =self._createUpdate()
        update.update[0].value.type = 3
        update.update[0].value.i = 12345

        with self.assertRaises(Exception) as context:
            self.dap1.update(update)

    def testNoTableUpdate(self):
        update = self._createUpdate()

        with self.assertRaises(Exception) as context:
            self.dap2.update(update)

