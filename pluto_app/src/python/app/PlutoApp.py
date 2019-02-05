import sys
from dap_api.src.python import DapManager
from ai_search_engine.src.python import SearchEngine
from dap_api.experimental.python import InMemoryDap
import api.src.python.ProtoWrappers as ProtoWrappers
from api.src.python.EndpointSearch import SearchQuery
from api.src.python.EndpointUpdate import UpdateEndpoint, BlkUpdateEndpoint
from api.src.python.BackendRouter import BackendRouter
from api.src.python.CommunicationHandler import run_socket_server, run_http_server
from concurrent.futures import ThreadPoolExecutor


class PlutoApp:
    def __init__(self):
        pass

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
        update_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.UpdateData, {
            "table": "data_model_table",
            "field": "data_model"
        })
        query_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.QueryData, self.dapManager)

        search_engine = self.dapManager.getInstance("data_model_searcher")

        # endpoints
        self._search_endpoint = SearchQuery(self.dapManager, query_wrapper)
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

    def run(self, http_port, socket_port, ssl_certificate, ):
        self.setup()
        self.executor.submit(run_socket_server, "0.0.0.0", socket_port, self.router)
        self.executor.submit(run_http_server, "0.0.0.0", http_port, ssl_certificate, self.router)
        self.executor.shutdown(wait=True)

    def getField(self, fieldname):
        return self.dapManager.getField(fieldname)

    def update(self, update):
        f = self.getField(update.update[0].fieldname)
        self.dapManager.getInstance(f['dap']).update(update)
