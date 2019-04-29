from network_oef.src.python.SearchNode import SearchNode
from ai_search_engine.src.python.SearchEngine import SearchEngine
from dap_api.src.python.network.DapNetworkProxy import proxy_config_from_dap_json, config_from_dap_json
import sys
import inspect
from utils.src.python.Logging import has_logger
from typing import List
import time


def _lookup(clss, name):
    for cls in clss:
        if cls[0] == name:
            return cls[1]
    return None


class FullSearchNone:

    @has_logger
    def __init__(self, node_name: str, ip: str, node_port: int, network_dap_config: List[dict], http_port: int = -1,
                 ssl_certificate: str = None, html_dir: str = None, *, director_api_port: int, log_dir: str = ""):
        """

        :param node_port: search node port
        :param network_dap_config: dict of dap name => port, config_file
        """
        classes = inspect.getmembers(sys.modules[__name__])

        self.daps = []
        tmp_dict = {}
        self.search_node = SearchNode(6, node_name)
        self.search_node.set_log_dir(log_dir)
        for conf in network_dap_config:
            if conf["run_mode"] == "PY":
                cs = config_from_dap_json(conf["file"])
                for ckey, c in cs.items():
                    c["config"]["host"] = "127.0.0.1"
                    c["config"]["port"] = conf["port"]
                    cls = _lookup(classes, c["class"])
                    if cls is None:
                        self.warning("Class not found: ", c["class"])
                        continue
                    self.daps.append(cls(ckey, c["config"]))
                cps = proxy_config_from_dap_json(conf["file"])
                for cpkey, cp in cps.items():
                    cp["config"]["port"] = conf["port"]
                    tmp_dict[cpkey] = cp
                time.sleep(1)
            elif conf["run_mode"] == "CPP":
                self.search_node.set_dap_port(conf["name"], conf["port"])
            else:
                self.error("Only PY/CPP DAP run modes supported!")
        self.search_node.init(ip, node_port, tmp_dict, http_port, ssl_certificate, html_dir, director_port=director_api_port)

    def add_remote_peer(self, host: str, port: int, node_id: str = None):
        self.search_node.connect_to_search_node(host, port, node_id)

    def disconnect_fom_search_network(self):
        self.search_node.disconnect()

    def block(self):
        self.search_node.block()