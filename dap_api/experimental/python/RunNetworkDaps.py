from dap_in_memory.src.python.InMemoryDap import InMemoryDap
from ai_search_engine.src.python.SearchEngine import SearchEngine
import sys
import inspect
from utils.src.python.Logging import configure as configure_logging
from dap_api.experimental.python.NetworkDapContract import config_backend as config


def lookup(clss, name):
    for cls in clss:
        if cls[0] == name:
            return cls[1]
    return None


configure_logging()
classes = inspect.getmembers(sys.modules[__name__])
daps = []

for name, conf in config.items():
    cls = lookup(classes, conf["class"])
    if cls is None:
        print("Class not found: ", conf["class"])
        continue
    daps.append(cls(name, conf["config"]))
