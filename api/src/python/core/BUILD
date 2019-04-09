py_library(
    name = "endpoints",
    srcs = glob(["*Endpoint.py"]),
    deps = [
        "//api/src/python:serialization",
        "//api/src/python:interfaces",
        "//api/src/proto/core:py_api_pb",
        "//utils/src/python:py_utils",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//ai_search_engine/src/python:search_engine"
    ],
    visibility = ["//visibility:public"],
)

py_library(
    name = "utils",
    srcs = ["ProtoWrappers.py"],
    deps = [
        "//dap_api/src/python:dap_api",
        "//dap_api/src/protos:py_dap_api_pb",
        "//api/src/proto/core:py_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//utils/src/python:py_utils",
    ],
    visibility = ["//visibility:public"],
)