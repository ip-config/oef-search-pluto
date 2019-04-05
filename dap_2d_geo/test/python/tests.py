import unittest

from dap_2d_geo.test.python.GeoStoreTest import GeoStoreTest
from dap_2d_geo.test.python.DapGeoTest import DapGeoTest

from utils.src.python.Logging import configure as configure_logging
configure_logging()

unittest.main() # run all tests
