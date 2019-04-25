import sys
import os

from dap_api.src.python import DapManager
from dap_api.src.python.network import DapNetworkProxy
from ai_search_engine.src.python import SearchEngine
from dap_in_memory.src.python import InMemoryDap
from dap_in_memory.src.python import AddressRegistry
from dap_in_memory.src.python import DataModelInstanceStore
from dap_attribute_store.src.python.DapAttributeStore import DapAttributeStore
import api.src.python.core.ProtoWrappers as ProtoWrappers
from api.src.python.RouterBuilder import CoreAPIRouterBuilder
from dap_2d_geo.src.python import DapGeo
from dap_e_r_network.src.python import DapERNetwork
from dap_api.experimental.python.NetworkDapContract import config_contract
from utils.src.python.Logging import has_logger


class PortInjector:
    def __init__(self):
        self.store = {}

    def get(self, name: str):
        value = self.store.get(name, -1)
        if value == -1:
            raise ValueError("DapPort not set for DAP: ", name)
        return value

    def set(self, name: str, value: int):
        self.store[name] = value


def _find__main__(path):
    while True:
        head, tail = os.path.split(path)
        if head == "":
            return ""
        if tail == "__main__":
            return path
        path = head


class PlutoApp:
    @has_logger
    def __init__(self):
        self.router = None
        self.dapManager = DapManager.DapManager()
        self._network_dap_config = dict()
        self._setup_endpoints()
        self._port_injector = PortInjector()
        self._log_dir = ""

    def addClass(self, name, maker):
        self.dapManager.addClass(name, maker)

    def add_network_dap_conf(self, name: str, config: dict):
        self._network_dap_config[name] = config

    def set_dap_port(self, name: str, port: int):
        self._port_injector.set(name, port)

    def set_log_dir(self, log_dir):
        self._log_dir = log_dir

    def setup(self, dapManagerConfig=None):
        if not dapManagerConfig:
            dapManagerConfig = {
                #"key_value_search": {
                #    "class": "InMemoryDap",
                #    "config": {
                #        "structure": {
                #            "value_table": {
                #                "*": "*"
                #            },
                #        },
                #    },
                #},
                "network_search": {
                    "class": "DapERNetwork",
                    "config": {
                        "structure": {
                            "locations": {
                                # actual fields generated by the store.
                            },
                        },
                    },
                },
                "geo_search": {
                    "class": "DapGeo",
                    "config": {
                        "structure": {
                            "location": {
                                # actual fields generated by the store.
                                "location.location": {
                                    "type": "location",
                                    "options": [
                                        "plane",
                                        "os-grid",
                                    ]
                                }
                            },
                        },
                    },
                },
                "address_registry": {
                    "class": "AddressRegistry",
                    "config": {
                        "structure": {
                            "address_registry_table": {
                                "address_field": "address"
                            },
                        },
                    },
                },
                #"in_memory_dap": {
                #    "class": "exe.InMemoryDap",
                #    "config": {
                #        "binary": "cpp_dap_in_memory/src/cpp/cpp_dap_in_memory_server",
                #        "host": "127.0.0.1",
                #        "port": self._port_injector.get("in_memory_dap"),
                #        "structure": {
                #            "value_table": {
                #                "field": "string"
                #            }
                #        }
                #    }
                #},
                #"attributes": {
                #    "class": "DapAttributeStore",
                #    "config": {
                #        "structure": {
                #        },
                #    },
                #},
                "data_model_searcher": {
                    "class": "SearchEngine",
                    "config": {
                        "structure": {
                            "data_model_table": {
                                "data_model": "embedding"
                            },
                        },
                    },
                },
                #"data_model_store": {
                #    "class": "DataModelInstanceStore",
                #    "config": {
                #        "structure": {
                #            "local_dm_table": {
                #                "data_model_2": "dm",
                #                "dm_values": "keyvalue"
                #            },
                #        },
                #    },
                #}
            }
            if len(self._network_dap_config) == 0 and "data_model_searcher" not in dapManagerConfig:
                dapManagerConfig["data_model_searcher"] = config_contract["data_model_searcher"]
            else:
                for name, config in self._network_dap_config.items():
                    dapManagerConfig[name] = config

        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig,
            _find__main__(os.path.abspath(os.path.dirname(__file__))),
            self._log_dir
        )

        self.dapManager.setDataModelEmbedder('data_model_searcher', 'data_model_table', 'data_model')

    def _setup_endpoints(self):
        AttrName = ProtoWrappers.AttributeName
        update_config = ProtoWrappers.ConfigBuilder(ProtoWrappers.UpdateData)\
            .data_model("data_model_table", "data_model")\
            .attribute(AttrName.Value("LOCATION"), "location_table", "coords")\
            .attribute(AttrName.Value("COUNTRY"), "location_table", "country")\
            .attribute(AttrName.Value("CITY"), "location_table", "city")\
            .attribute(AttrName.Value("NETWORK_ADDRESS"), "address_registry_table", "address_field")\
            .default("default_table", "default_field")\
            .data_model_2("local_dm_table", "data_model_2")\
            .dm_values("local_dm_table", "dm_values")\
            .build()

        update_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.UpdateData, update_config)
        query_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.QueryData, self.dapManager)

        self.router = CoreAPIRouterBuilder()\
            .set_name("PlutoAppMainRouter")\
            .add_dap_manager(self.dapManager)\
            .add_search_wrapper(query_wrapper)\
            .add_update_wrapper(update_wrapper)\
            .build()

    def add_handler(self, path, handler):
        self.router.register_handler(path, handler)

    def start(self, com=None):
        self.setup()
        if com is not None:
            com.start(self.router)

    def inject_w2v(self, w2v):
        search_engine = self.dapManager.getInstance("data_model_searcher")
        search_engine.inject_w2v(w2v)

    async def callMe(self, path, data):
        response = await self.router.route(path, data)
        if not response.success:
            self.error("callMe error: code=", response.error_code, ", narrative=", response.narrative)
        return response.data

