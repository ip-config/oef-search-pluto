import unittest
from utils.src.python.Logging import configure as configure_logging

from pluto_app.test.python.PlutoTest import PlutoTest
#from dap_api.test.python.QueryTest import QueryTest
#from dap_api.test.python.QueryEmbeddingsTest import QueryEmbeddingsTest
#from dap_api.test.python.DapManagerTest import DapManagerTest

configure_logging()
unittest.main() # run all tests
