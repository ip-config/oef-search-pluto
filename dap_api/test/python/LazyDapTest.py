import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_api.src.python import DapQueryRepn
from dap_in_memory.src.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_2d_geo.src.python import DapGeo
from dap_attribute_store.src.python import DapAttributeStore
from dap_api.src.python import ProtoHelpers

class LazyDapTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        pass

    def testFieldOptionsWork(self):
        dapManager = DapManager.DapManager()

        dapManagerConfig = {
            "geo": {
                "class": "DapGeo",
                "config": {
                    "structure": {
                        "wobbles": {
                            "location": {
                                "type": "location",
                                "options": [
                                    "plane",
                                ]
                            }
                        },
                    },
                },
            },
            "attrs": {
                "class": "DapAttributeStore",
                "config": {
                    "structure": {
                    },
                },
                "options": [
                    "lazy",
                ],
            },
            "annotations": {
                "class": "InMemoryDap",
                "config": {
                    "structure": {
                        "annotations": {
                            "name": "string",
                            "id": "int64",
                        },
                    },
                },
            },
        }
        dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)


        DATA = [
            ("007/James/Bond",   (51.477,-0.461),  [('id',1), ('foo',1)], ), # LHR
            ("White/Spy",        (53.354,-2.275),  [('id',2), ('foo',2)], ), # MANCHESTER
            ("Black/Spy",        (50.734,-3.414),  [('id',3), ('foo',3)], ), #EXETER
            ("86/Maxwell/Smart", (40.640,-73.779), [('id',4), ('foo',4)], ), # JFK
        ]

        lat = 0
        lon = 0
        count = 1
            #update = dap_update_pb2.DapUpdate()
            #update.update.add()
            #update.update[0].fieldname = "location"
            #update.update[0].key.core = b'localhost'
            #update.update[0].key.agent = agent.encode("utf-8")
            #update.update[0].value.l.lat = loc[0]
            #update.update[0].value.l.lon = loc[1]
            #update.update[0].value.type = 9
            #dapManager.update(update)

        for agent, loc, attrs in DATA:
            update = dap_update_pb2.DapUpdate()
            for (k,v) in attrs[0:1]:
                u = update.update.add()
                u.key.core = b'localhost'
                u.key.agent = agent.encode("utf-8")
                ProtoHelpers.populateUpdateTFV(u, k, v)
            dapManager.update(update)
            break

        # we're going to check that when the assignments to the "id"
        # field were routed, they did not go to the attribute store.

        assert dapManager.getInstance("attrs").table == {}

        for agent, loc, attrs in DATA:
            update = dap_update_pb2.DapUpdate()
            for (k,v) in attrs[1:]:
                u = update.update.add()
                u.key.core = b'localhost'
                u.key.agent = agent.encode("utf-8")
                ProtoHelpers.populateUpdateTFV(u, k, v)
            dapManager.update(update)
            break

        # But "foo" should have been...

        assert dapManager.getInstance("attrs").table != {}

