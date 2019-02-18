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
    ],
)
