from dap_api.experimental.python.InMemoryDap import InMemoryDap
import sys
import inspect
from utils.src.python.Logging import configure as configure_logging
from dap_api.experimental.python.NetworkDapContract import contract_config


def lookup(clss, name):
    for cls in clss:
        if cls[0] == name:
            return cls[1]
    return None


configure_logging()
classes = inspect.getmembers(sys.modules[__name__])
daps = []
for name, conf in contract_config.items():
    cls = lookup(classes, conf["class"])
    daps.append(cls(name, conf["config"]))
