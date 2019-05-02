import sys
import unittest

from dap_api.src.python import DapManager
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python import ProtoHelpers

from dap_api.src.python import DapQuery

from dap_2d_geo.src.python.DapGeo import DapGeo

def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


class PlutoTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        config = {
            "locations": {
                "class": "DapGeo",
                "config": {
                    "structure": {
                        "airports": {
                            "airports": {
                                "type": "location"
                            }
                        },
                    },
                },
            },
        }

        self.data = DapManager.DapManager()
        #self.data.addClass("DapGeo", DapGeo.DapGeo)
        self.data.setup(sys.modules[__name__], config)

        self.setupAirports()
        self.BHX = (52.454, -1.748)

    def setupAirports(self):
        g = self.data.getInstance("locations").getGeoByTableName("airports")
        with open("dap_2d_geo/test/resources/GlobalAirportDatabase.txt", "r") as f:
            for i in f.readlines():
                i = i.strip()
                parts = i.split(":")

                if len(parts)<16:
                    continue

                airport = parts[1]
                country = parts[4]

                lat = float(parts[14])
                lon = float(parts[15])

                if airport == 'N/A':
                    continue

                if lat == 0.0 and lon == 0.0:
                    continue

                ident = ( b"localhost",  ("{}/{}".format(airport, country)).encode('utf-8') )
                loc = (lat, lon)

                g.place(ident, loc)

    def test25KmAroundBirmingham(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()

        qc = qm.constraints.add()

        q1 = qc.and_.expr.add()
        q2 = qc.and_.expr.add()

        q1.constraint.attribute_name = "airports.location"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.l.lat = self.BHX[0]
        q1.constraint.relation.val.l.lon = self.BHX[1]

        q2.constraint.attribute_name = "airports.radius"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.d = 25000

        dapQuery = self.data.makeQuery(qm)
        identifierSequence = self.data.execute(dapQuery)
        results = [ x.agent.decode('utf8') for x in identifierSequence.identifiers ]

        assert sorted(results) == ['BHX/ENGLAND', 'CVT/ENGLAND']

    def test200KmAroundBirmingham(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()

        qc = qm.constraints.add()

        q1 = qc.and_.expr.add()
        q2 = qc.and_.expr.add()

        q1.constraint.attribute_name = "airports.location"
        q1.constraint.relation.op = 0
        q1.constraint.relation.val.l.lat = self.BHX[0]
        q1.constraint.relation.val.l.lon = self.BHX[1]

        q2.constraint.attribute_name = "airports.radius"
        q2.constraint.relation.op = 0
        q2.constraint.relation.val.d = 200000

        dapQuery = self.data.makeQuery(qm)
        identifierSequence = self.data.execute(dapQuery)
        results = [ x.agent.decode('utf8') for x in identifierSequence.identifiers ]

        assert sorted(results) == [
            'BBS/ENGLAND',
            'BEQ/ENGLAND',
            'BHX/ENGLAND',
            'BLK/ENGLAND',
            'BOH/ENGLAND',
            'BQH/ENGLAND',
            'BRS/ENGLAND',
            'BZZ/ENGLAND',
            'CBG/ENGLAND',
            'CEG/ENGLAND',
            'CVT/ENGLAND',
            'CWL/WALES',
            'EMA/ENGLAND',
            'FAB/ENGLAND',
            'FFD/ENGLAND',
            'FZO/ENGLAND',
            'GLO/ENGLAND',
            'HTF/ENGLAND',
            'HUY/ENGLAND',
            'KNF/UK',
            'LBA/ENGLAND',
            'LCY/ENGLAND',
            'LGW/ENGLAND',
            'LHR/ENGALND',
            'LPL/ENGLAND',
            'LTN/ENGLAND',
            'LYE/UK',
            'MAN/ENGLAND',
            'MHZ/ENGLAND',
            'NHT/UK',
            'ODH/UK',
            'OXF/ENGLAND',
            'QCY/ENGLAND',
            'QLA/ENGLAND',
            'SEN/ENGLAND',
            'SOU/ENGLAND',
            'STN/ENGLAND',
            'SWS/ENGLAND',
            'WTN/UK',
            'YEO/UK',
        ]

unittest.main() # run all tests
