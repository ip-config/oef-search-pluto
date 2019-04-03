import os
from dap_api.src.python.network.DapNetworkProxy import proxy_config_from_dap_json, config_from_dap_json

_JSON_DIRS = [
    "cpp-sdk/experimental/resources/",
    "ai_search_engine/src/resources/"
]

json_configs = []
for d in _JSON_DIRS:
    json_configs.extend([d+f for f in os.listdir(d) if f.find(".json") != -1])


config_contract = {}
for file in json_configs:
    c = proxy_config_from_dap_json(file)
    config_contract = {**config_contract, **c}

config_backend = {}
for file in json_configs:
    c = config_from_dap_json(file)
    config_backend = {**config_backend, **c}
