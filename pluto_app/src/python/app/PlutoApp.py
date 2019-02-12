import argparse
import sys

from dap_api.src.python import DapManager
from ai_search_engine.src.python import SearchEngine
from dap_api.experimental.python import InMemoryDap
from dap_api.experimental.python import AddressRegistry
import api.src.python.ProtoWrappers as ProtoWrappers
from api.src.python.EndpointSearch import SearchQuery
from api.src.python.EndpointUpdate import UpdateEndpoint, BlkUpdateEndpoint
from api.src.python.BackendRouter import BackendRouter
from api.src.python.CommunicationHandler import run_socket_server, run_http_server
from concurrent.futures import ThreadPoolExecutor


class PlutoApp:
    def __init__(self):
        self.args = None

    def setup(self, dapManagerConfig=None):
        self.dapManager = DapManager.DapManager()
        if not dapManagerConfig:
            dapManagerConfig = {
                "dap1": {
                    "class": "InMemoryDap",
                    "config": {
                        "structure": {
                            "wibbles": {
                                "wibble": "string"
                            },
                        },
                    },
                },
                "dap2": {
                    "class": "InMemoryDap",
                    "config": {
                        "structure": {
                            "wobbles": {
                                "wobble": "string"
                            },
                        },
                    },
                },
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
                "address_registry": {
                    "class": "AddressRegistry",
                    "config": {
                        "structure": {
                            "address_registry_table": {
                                "address_field": "address"
                            },
                        },
                    },
                }
            }

        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig
        )

        self.dapManager.setDataModelEmbedder('data_model_searcher', 'data_model_table', 'data_model')

        self._setup_endpoints()
        self._setup_router()

        self.executor = ThreadPoolExecutor(max_workers=2)

    def _setup_endpoints(self):
        AttrName = ProtoWrappers.AttributeName
        update_config = ProtoWrappers.ConfigBuilder(ProtoWrappers.UpdateData)\
            .data_model("data_model_table", "data_model")\
            .attribute(AttrName.Value("LOCATION"), "location_table", "coords")\
            .attribute(AttrName.Value("COUNTRY"), "location_table", "country")\
            .attribute(AttrName.Value("CITY"), "location_table", "city")\
            .attribute(AttrName.Value("NETWORK_ADDRESS"), "address_registry_table", "address_field")\
            .default("default_table", "default_field")\
            .build()

        address_registry = self.dapManager.getInstance("address_registry")

        update_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.UpdateData, update_config, address_registry)
        query_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.QueryData, self.dapManager)

        search_engine = self.dapManager.getInstance("data_model_searcher")

        # endpoints
        self._search_endpoint = SearchQuery(self.dapManager, query_wrapper, address_registry)
        self._update_endpoint = UpdateEndpoint(self.dapManager, update_wrapper)
        self._blk_update_endpoint = BlkUpdateEndpoint(self.dapManager, update_wrapper)

    def _setup_router(self):
        # router
        self.router = BackendRouter()
        self.router.register_serializer("search", self._search_endpoint)
        self.router.register_handler("search",  self._search_endpoint)
        self.router.register_serializer("update",  self._update_endpoint)
        self.router.register_handler("update",  self._update_endpoint)
        self.router.register_serializer("blk_update",  self._blk_update_endpoint)
        self.router.register_handler("blk_update",  self._blk_update_endpoint)

    def run(self):
        parser = argparse.ArgumentParser(description='Test application for PLUTO.')
        parser.add_argument("--ssl_certificate",  required=True, type=str, help="specify an SSL certificate PEM file.")
        parser.add_argument("--http_port",        required=True, type=int, help="which port to run the HTTP interface on.")
        parser.add_argument("--socket_port",      required=True, type=int, help="which port to run the socket interface on.")
        self.args = parser.parse_args()

        self.setup()
        self.executor.submit(run_socket_server, "0.0.0.0", self.args.socket_port, self.router)
        self.executor.submit(run_http_server, "0.0.0.0", self.args.http_port, self.args.ssl_certificate, self.router)
        self.executor.shutdown(wait=True)

    def getField(self, fieldname):
        return self.dapManager.getField(fieldname)

