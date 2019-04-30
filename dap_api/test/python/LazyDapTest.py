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

class DapManagerMoreTest(unittest.TestCase):
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
                            "wobbles.location": {
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
                    },
            },
        }
        dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

        lat = 0
        lon = 0
        count = 1
        for agent, loc in [
            ("007/James/Bond",   (51.477,-0.461)  (),), # LHR
            ("White/Spy",        (53.354,-2.275)  ()), # MANCHESTER
            ("Black/Spy",        (50.734,-3.414)  ()), #EXETER
            ("86/Maxwell/Smart", (40.640,-73.779) ()), # JFK
        ]:
            update = dap_update_pb2.DapUpdate()
            update.update.add()
            update.update[0].tablename = "wobbles"
            update.update[0].fieldname = "location.update"
            update.update[0].key.core = b'localhost'
            update.update[0].key.agent = agent.encode("utf-8")
            update.update[0].value.l.lat = loc[0]
            update.update[0].value.l.lon = loc[1]
            update.update[0].value.type = 9
            dapManager.update(update)

            lat += loc[0]
            lon += loc[1]
            count += 1

        lat /= count
        lon /= count

        update = dap_update_pb2.DapUpdate()
        update.update.add()
        update.update[0].tablename = "wobbles"
        update.update[0].fieldname = "wobbles.update"
        update.update[0].key.core = b'localhost'
        update.update[0].value.l.lat = lat
        update.update[0].value.l.lon = lon
        update.update[0].value.type = 9
        dapManager.update(update)

