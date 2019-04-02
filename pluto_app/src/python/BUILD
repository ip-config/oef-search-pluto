py_binary(
    name = "pluto",
    srcs = ["main/main.py"],
    main = "main/main.py",
    visibility = ["//visibility:public"],
    deps = [
        "//ai_search_engine/src/python:search_engine",
        "//dap_api/src/protos:py_dap_api_pb",
        "//dap_api/src/python:dap_api",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//pluto_app/src/python/app:app",
        "//utils/src/python:py_utils",
        "//dap_api/experimental/python:network_dap_contract",
        "//dap_in_memory/src/python:dap_in_memory",
        "//dap_api/src/python/network:dap_network"
    ],
)

py_binary(
    name = "pluto_central",
    srcs = ["main/central.py"],
    main = "main/central.py",
    visibility = ["//visibility:public"],
    deps = [
        "//ai_search_engine/src/python:search_engine",
        "//dap_api/src/protos:py_dap_api_pb",
        "//dap_api/src/python:dap_api",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//pluto_app/src/python/app:app",
        "//utils/src/python:py_utils",
    ],
)
