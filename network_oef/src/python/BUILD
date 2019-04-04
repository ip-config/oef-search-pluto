py_library(
    name="lib",
    visibility = ["//visibility:public"],
    srcs = glob(["*.py"]),
    deps = [
        "//dap_api/src/python:dap_api",
        "//dap_api/src/python/network:dap_network",
        "//ai_search_engine/src/python:search_engine",
        "//api/src/proto/core:py_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//utils/src/python:py_utils",
        "//network/src/python/async_socket:async_socket",
        "//pluto_app/src/python/app:app"
    ],
    data = [
    ],
)
