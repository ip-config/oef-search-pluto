#!/usr/bin/env python3

import sys
import unittest
import json
import subprocess
import os
import time

from dap_api.src.python import DapManager
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python import ProtoHelpers
from dap_api.src.python import DapQuery
from google.protobuf import json_format
from dap_api.src.python.network import DapNetworkProxy
from utils.src.python.Logging import has_logger

class CppInMemoryDapTest(unittest.TestCase):
    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Call before every test case."""

        self.dapManager = DapManager.DapManager()
        dapManagerConfig = {
            "dap1": {
                "class": "DapNetworkProxy",
                "config": {
                    "structure": {
                        "media": {
                            "media": "string"
                        },
                        "nation": {
                            "nation": "string"
                        },
                    },
                    "host": "127.0.0.1",
                    "port": 15000
                },
            }
        }

        self.remoteProcessConfig = """
{
    "host": "127.0.0.1",
    "port": 15000,
    "description": {
        "name": "dap1",
        "table": [
            {
                "name": "media",
                "field": [
                    {
                        "name": "media",
                        "type": "string"
                    }
                ]
            }, {
                "name": "nation",
                "field": [
                    {
                        "name": "nation",
                        "type": "string"
                    }
                ]
            }
        ]
    }
}
"""
        self.remoteProcessArgs = [
            "cpp_dap_in_memory/src/cpp/cpp_dap_in_memory_server", "--configjson", self.remoteProcessConfig,
            #'find', '.', "-name", "cpp_dap_in_memory_server",
            #'bazel-bin/cpp_dap_in_memory/src/cpp/cpp_dap_in_memory_server.runfiles/__main__/cpp_dap_in_memory/src/cpp/cpp_dap_in_memory_server',
            #'--help',
        ]
        self.remoteProcess = subprocess.Popen(self.remoteProcessArgs)
        time.sleep(0.25)

        self.dapManager.setup(sys.modules[__name__], dapManagerConfig)
        self.dap1 = self.dapManager.getInstance("dap1")

    def tearDown(self):
        self.remoteProcess.terminate()
        self.remoteProcess.wait()


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

            self.warning(str(update))

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

    def testQueryAnd(self):
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
