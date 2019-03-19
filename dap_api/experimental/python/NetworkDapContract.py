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