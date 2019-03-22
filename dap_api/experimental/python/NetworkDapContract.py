import json
import os

_JSON_DIR = "cpp-sdk/experimental/resources/"

json_configs = [_JSON_DIR+f for f in os.listdir(_JSON_DIR) if f.find(".json") != -1]


def config_from_dap_json(file):
    f = open(file)
    j = json.load(f)

    config = dict()
    c = config[j["description"]["name"]] = dict()

    c["class"] = "DapNetworkProxy"
    c["config"] = dict()
    c["config"]["host"] = j["host"]
    c["config"]["port"] = j["port"]
    c["config"]["structure"] = dict()

    cs = c["config"]["structure"]

    tb = j["description"]["table"]
    if tb:
        cs[tb["name"]] = dict()
        for f in tb["field"]:
            cs[tb["name"]][f["name"]] = f["type"]
    return config


config_backend = {
"data_model_searcher": {
    "class": "SearchEngine",
    "config": {
        "structure": {
            "data_model_table": {
                "data_model": "embedding"
            },
        },
        "host": "127.0.0.1",
        "port": 15000
    },
},
}

config_contract = {
    "data_model_searcher": {
        "class": "DapNetworkProxy",
        "config": config_backend["data_model_searcher"]["config"]
    }
}

for file in json_configs:
    c = config_from_dap_json(file)
    config_contract = {**config_contract, **c}