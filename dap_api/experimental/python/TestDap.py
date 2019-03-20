from dap_api.src.python.network.DapNetworkProxy import DapNetworkProxy
import sys
import inspect
from dap_api.experimental.python.NetworkDapContract import config_contract
from utils.src.python.Logging import configure as configure_logging


selected_ports = [7600]


def lookup(clss, name):
    for cls in clss:
        if cls[0] == name:
            return cls[1]
    return None

configure_logging()
classes = inspect.getmembers(sys.modules[__name__])
daps = []
for name, conf in config_contract.items():
    cls = lookup(classes, conf["class"])
    if cls is not None and conf["config"]["port"] in selected_ports:
        daps.append(cls(name, conf["config"]))
        dap = daps[-1]
        print(dap.describe())
