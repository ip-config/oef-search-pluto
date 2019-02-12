
import unittest
import sys

from dap_2d_geo.src.python import GeoStore

class GeoStoreTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        self.g = GeoStore.GeoStore()

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

                if parts[1] == 'N/A':
                    continue

                if lat == 0.0 and lon == 0.0:
                    continue

                self.g.place("{}/{}".format(airport, country), (lat, lon))

        self.BHX = (52.454, -1.748)

    def testBasic(self):
        r = list(self.g.search(self.BHX, 2.0))
        assert sorted(r) == [
            'BBS/ENGLAND',
            'BHX/ENGLAND',
            'BLK/ENGLAND',
            'BOH/ENGLAND',
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
            'HUY/ENGLAND',
            'LBA/ENGLAND',
            'LHR/ENGALND',
            'LPL/ENGLAND',
            'LTN/ENGLAND',
            'LYE/UK',
            'MAN/ENGLAND',
            'NHT/UK',
            'ODH/UK',
            'OXF/ENGLAND',
            'QCY/ENGLAND',
            'QLA/ENGLAND',
            'SOU/ENGLAND',
            'WTN/UK',
            'YEO/UK',
        ]
