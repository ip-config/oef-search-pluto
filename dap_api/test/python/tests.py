import unittest

from dap_api.test.python.UpdateTest import UpdateTest
#from dap_api.test.python.QueryEmbeddingsTest import QueryEmbeddingsTest


from dap_api.test.python.QueryTest import QueryTest
from dap_api.test.python.DapManagerTest import DapManagerTest
from dap_api.test.python.DapManagerMoreTest import DapManagerMoreTest

from utils.src.python.Logging import configure as configure_logging
configure_logging()

unittest.main() # run all tests
