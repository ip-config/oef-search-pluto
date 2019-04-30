import unittest

# This doesn't work at all and hasn't for yonks
#from dap_api.test.python.QueryEmbeddingsTest import QueryEmbeddingsTest


from dap_api.test.python.UpdateTest import UpdateTest
from dap_api.test.python.QueryTest import QueryTest
from dap_api.test.python.DapManagerTest import DapManagerTest
from dap_api.test.python.DapManagerMoreTest import DapManagerMoreTest
from dap_api.test.python.QueryDapFiltersTest import QueryDapFiltersTest

from dap_api.test.python.LazyDapTest import LazyDapTest

from utils.src.python.Logging import configure as configure_logging
configure_logging()

unittest.main() # run all tests
