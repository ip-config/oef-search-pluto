
import unittest
import sys
import json

from dap_2d_geo.src.python import GeoStore

class GeoStoreTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        self.g = GeoStore.GeoStore()
        self.BHX = (52.454, -1.748)
        self.NQY = (50.440, -5)
        self.CVT = (52.369, -1.48)

    def add(self, limit=None):
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

                if limit != None:
                    if airport not in limit:
                        continue

                if lat == 0.0 and lon == 0.0:
                    continue

                #print("{}/{}".format(airport, country), lat, lon)

                self.g.place("{}/{}".format(airport, country), (lat, lon))

    def testBasic(self):
        self.add(limit = [
            'CVT',
            'BHX',
            'LHR',
            'YEO',
            'JFK',
        ])

        r = list(self.g.searchWithData(self.BHX, 25000))

        r = [
            (entity, int(dist/1000))
            for (entity, dist, br) in r
        ]

        assert ('CVT/ENGLAND', 20) in r

    def testBearings1(self):
        self.add(limit = [
            'CVT',
            'BHX',
            'LHR',
            'YEO',
            'JFK',
        ])

        r = list(self.g.searchWithData(self.BHX, 250000))

        output = sorted(r, key=lambda x: x[0])
        expected = [
            ('BHX/ENGLAND', 0, 0),
            ('CVT/ENGLAND', 20436, 117),
            ('LHR/ENGALND', 139916, 140),
                 # Yes, misspelled in data.
            ('YEO/UK', 171994, 201),
        ]
        #print(output)
        #print(expected)

        assert output == expected

    def testBasic2(self):
        self.add(limit = [
            'CVT',
            'BHX',
            'LHR',
            'YEO',
            'JFK',
        ])
        r = list(self.g.search(self.BHX, 250000))

        assert sorted(r) == [
            'BHX/ENGLAND',
            'CVT/ENGLAND',
            'LHR/ENGALND', # Yes, misspelled in data.
            'YEO/UK',
        ]

    def testBiggerWithBearings(self):
        self.add()
        r = sorted(list(self.g.searchWithData(self.BHX, 400000, bearing=0, bearing_width=20)), key=lambda x: x[0])
        expected = [
            ('BHX/ENGLAND', 0, 0),
            ('CAX/ENGLAND', 284903, 346),
            ('LBA/ENGLAND', 157114, 2),
            ('MME/ENGLAND', 229478, 5),
            ('NCL/ENGLAND', 287351, 0)
        ]
        assert sorted(r) == expected

    def testBearings(self):
        nqy = GeoStore.GeoStore.InitialBearing(self.BHX, self.NQY)
        cvt = GeoStore.GeoStore.InitialBearing(self.BHX, self.CVT)

        assert nqy == 226
        assert cvt == 117

        assert GeoStore.GeoStore.containsBearing(270, 90, 0) == True
        assert GeoStore.GeoStore.containsBearing(270, 90, 95) == False

    def testBigger(self):
        self.add()
        expected = [
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

        r = list(self.g.search(self.BHX, 200000))

        assert sorted(r) == expected
