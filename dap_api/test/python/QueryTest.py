import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_in_memory.src.python import InMemoryDap
from dap_in_memory.src.python import EarlyInMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger

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

    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Call before every test case."""

        self.dapManager = DapManager.DapManager()

        dapManagerConfig = {
            "dap1": {
                "class": "InMemoryDap",
                "config": {
                    "structure": {
                        "media": {
                            "media": "string"
                        },
                    },
                },
            },
            "dap-early": {
                "class": "EarlyInMemoryDap",
                "config": {
                    "structure": {
#                        "wibbles": {
#                            "wibble": "string"
#                        },
#                        "wobbles": {
#                            "wobble": "string"
#                        },
                    },
                },
            },
            "dap2": {
                "class": "InMemoryDap",
                "config": {
                    "structure": {
                        "nation": {
                            "nation": "string"
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
        newvalue.key.core = b"localhost"
        return update

    def _setupAgents(self):
        for agent, media in [
            ("007/James/Bond",   "tv/film"), # Yes, I know James Bond was originally in books.
            ("White/Spy",        "comics"),
            ("Black/Spy",        "comics"),
            ("86/Maxwell/Smart", "tv/film"),
        ]:
            update = self._createUpdate()
            update.update[0].tablename = "media"
            update.update[0].fieldname = "media"
            update.update[0].key.agent = agent.encode("utf-8")
            update.update[0].value.s = media
            update.update[0].value.type = 2
            self.dapManager.update(update)

        for agent, nation in [
            ("007/James/Bond",   "UK"),
            ("White/Spy",        "UK"),
            ("Black/Spy",        "UK"),
            ("86/Maxwell/Smart", "America"),
        ]:
            update = self._createUpdate()
            update.update[0].tablename = "nation"
            update.update[0].fieldname = "nation"
            update.update[0].value.s = nation
            update.update[0].value.type = 2
            update.update[0].key.agent = agent.encode("utf-8")
            self.dapManager.update(update)


    def testQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self.info("=======================================================================")
        self.info("testQuery")
        self._setupAgents()

        qm = query_pb2.Query.Model()
        q = qm.constraints.add()

        q.constraint.attribute_name = "media"
        q.constraint.relation.op = 0
        q.constraint.relation.val.s = "comics"

        dapQuery = self.dapManager.makeQuery(qm)
        results = list(self.dapManager.execute(dapQuery).identifiers)
        assert len(results) == 2

    def testQueryOr(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self.info("=======================================================================")
        self.info("testQueryOr")
        self._setupAgents()

        qm = query_pb2.Query.Model()
        qOr = qm.constraints.add()

        q1 = qOr.or_.expr.add()
        q2 = qOr.or_.expr.add()

        q1.constraint.attribute_name = "media"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "comics"

        q2.constraint.attribute_name = "nation"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.s = "America"


        dapQuery = self.dapManager.makeQuery(qm)
        output = self.dapManager.execute(dapQuery)
        results = list(output.identifiers)
        assert len(results) == 3
        assert output.HasField("status") == False

    def testQueryAnd(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self.info("=======================================================================")
        self.info("testQueryAnd")
        self._setupAgents()

        qm = query_pb2.Query.Model()
        qAnd = qm.constraints.add()

        q1 = qAnd.and_.expr.add()
        q2 = qAnd.and_.expr.add()

        q1.constraint.attribute_name = "media"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "tv/film"

        q2.constraint.attribute_name = "nation"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.s = "UK"


        dapQuery = self.dapManager.makeQuery(qm)
        output = self.dapManager.execute(dapQuery)
        results = list(output.identifiers)
        assert len(results) == 1
        assert output.HasField("status") == False

    def testQueryCanFail(self):
        self.info("=======================================================================")
        self.info("testQueryCanFail")
        qm = query_pb2.Query.Model()
        qOr = qm.constraints.add()

        q1 = qOr.or_.expr.add()
        q2 = qOr.or_.expr.add()

        q1.constraint.attribute_name = "wibble"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.s = "carrot"

        q2.constraint.attribute_name = "____INVALID_FIELD_NAME"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.s = "apple"


        dapQuery = self.dapManager.makeQuery(qm)
        output = self.dapManager.execute(dapQuery)
        results = list(output.identifiers)
        assert len(results) == 0
        assert output.status.success == False
        assert len(output.status.narrative) == 1

        self.error("We expect an error report at this point...")
        self.error("Error report? -- ", output.status.narrative[0])
