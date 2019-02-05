import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from ai_search_engine.src.python import SearchEngine
from dap_api.experimental.python import InMemoryDap

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
                                "data_model_field": "embedding"
                            },
                        },
                    },
                },
            }

        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig
        )

        self.dapManager.setDataModelEmbedder('data_model_searcher', 'data_model_table', 'data_model_field')

    def run(self):
        self.setup()
        print("Setup done.")

    def getField(self, fieldname):
        return self.dapManager.getField(fieldname)

    def update(self, update):
        f = self.getField(update.update[0].fieldname)
        self.dapManager.getInstance(f['dap']).update(update)
