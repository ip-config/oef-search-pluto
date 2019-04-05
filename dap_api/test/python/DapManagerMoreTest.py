import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_api.src.python import DapQueryRepn
from dap_in_memory.src.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_2d_geo.src.python import DapGeo

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
        }
        dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

        lat = 0
        lon = 0
        count = 1
        for agent, loc in [
            ("007/James/Bond",   (51.477,-0.461)), # LHR
            ("White/Spy",        (53.354,-2.275)), # MANCHESTER
            ("Black/Spy",        (50.734,-3.414)), #EXETER
            ("86/Maxwell/Smart", (40.640,-73.779)), # JFK
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

        r = dapManager.getInstance("geo").describe()
        nameToField = {}
        for f in r.table[0].field:
            nameToField[f.name] = {
                "type": f.type,
                "options": f.options,
            }
        assert 'plane' in nameToField["wobbles.location"]["options"]
        assert nameToField["wobbles.location"]["type"] == "location"

        r = dapManager.getPlaneInformation('location')
        assert r['field_name'] == 'wobbles.location'
        assert len(r['values']) == 1

        assert r['values'][0].key.core == b'localhost'
        assert int(r['values'][0].value.l.lon) == -15
        assert int(r['values'][0].value.l.lat) == 39
