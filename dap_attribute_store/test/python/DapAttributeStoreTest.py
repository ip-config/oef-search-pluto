
import unittest
import sys
import json

from dap_attribute_store.src.python import DapAttributeStore
from dap_api.src.python import DapManager
from dap_api.src.protos import dap_update_pb2
from api.src.proto import update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger

class DapAttributeStoreTest(unittest.TestCase):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Call before every test case."""

        self.dapManager = DapManager.DapManager()

        dapManagerConfig = {
            "attributes": {
                "class": "DapAttributeStore",
                "config": {
                    "structure": {
                    },
                },
            },
        }
        self.dapManager.setDataModelEmbedder("", "", "")
        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

        for agent, list_of_attr_val_type_tuples in [
            (
                "007/James/Bond",
                [
                    ("fave-gun", "string", "waltherppk")
                ],
            ),
            (
                "007/James/Bond",
                [
                    ("licence", "string", "to-kill")
                ],
            ),
            (
                "santa",
                [
                    ("busiest-day", "string", "25 december")
                ],
            ),
            (
                "this bloody office",
                [
                    ("temperature", "double", 23.9)
                ],
            ),
        ]:
            self.error(agent)
            self.dapManager.update(self.CreateUpdateForAgent(agent, list_of_attr_val_type_tuples))

    def CreateUpdateForAgent(self, agent, list_of_attr_val_type_tuples):
        upd = dap_update_pb2.DapUpdate.TableFieldValue()
        upd.tablename = 'moocows'
        upd.fieldname = 'them.temperature'
        upd.key.core = b'localhost'
        upd.key.agent = agent.encode("utf-8")
        upd.value.type = 11
        upd.value.kv.extend([
            self.CreateKVForUpdate(x[0], x[1], x[2])
            for x
            in list_of_attr_val_type_tuples
        ])
        return upd

    def CreateKVForUpdate(self, attr_name, attr_type, attr_data):
        r = query_pb2.Query.KeyValue()
        r.key = "them." + attr_name
        if attr_type == "string":
            r.value.s = str(attr_data)
        elif attr_type == "double":
            r.value.d = float(attr_data)
        elif attr_type == "int64":
            r.value.i = int(attr_data)
        else:
            raise Exception("Don't support type " + attr_type + " in test setup")
        return r

    def testUpdatesWorked(self):
        self.info("=======================================================================")
        self.info("testQuerytestUpdatesWorked")

        store = self.dapManager.getInstance("attributes")
        assert len(store.table) > 0

        store.print()

        qm = query_pb2.Query.Model()
        q = qm.constraints.add()

        q.constraint.attribute_name = "them.fave-gun"
        q.constraint.relation.op = 0
        q.constraint.relation.val.s = "waltherppk"

        dapQuery = self.dapManager.makeQuery(qm)
        results = list(self.dapManager.execute(dapQuery).identifiers)

        self.warning("results:", len(results))
        for r in results:
            self.warning(r)
        assert len(results) == 1

        assert results[0].agent == b"007/James/Bond"
