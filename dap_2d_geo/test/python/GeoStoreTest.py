
import unittest
import sys
import json

from dap_2d_geo.src.python import GeoStore

class GeoStoreTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        self.g = GeoStore.GeoStore()
        self.BHX = (52.454, -1.748)

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

        r = list(self.g.searchWithDistances(self.BHX, 25000))

        r = [
            (entity, int(dist/1000))
            for (entity, dist) in r
        ]

        assert ('CVT/ENGLAND', 20) in r

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

