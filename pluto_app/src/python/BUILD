py_binary(
    name = "pluto",
    srcs = ["main/main.py"],
    main = "main/main.py",
    visibility = ["//visibility:public"],
    deps = [
        "//pluto_app/src/python/app:app",
        "//dap_api/src/python:dap_api",
        "//ai_search_engine/src/python:search_engine",
        "//dap_api/src/protos:py_dap_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
    ],
)
