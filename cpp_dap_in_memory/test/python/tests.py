import unittest

from cpp_dap_in_memory.test.python.CppInMemoryDapTest import CppInMemoryDapTest

from utils.src.python.Logging import configure as configure_logging
configure_logging()

unittest.main() # run all tests
