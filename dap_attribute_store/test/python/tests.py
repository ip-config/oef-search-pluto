import unittest

from dap_attribute_store.test.python.DapAttributeStoreTest import DapAttributeStoreTest

from utils.src.python.Logging import configure as configure_logging
configure_logging()
unittest.main() # run all tests
