py_library(
    name = "endpoints",
    srcs = glob(["*Endpoint.py"]),
    deps = [
        "//api/src/python:serialization",
        "//api/src/python:interfaces",
        "//api/src/proto/director:py_api_pb",
        "//utils/src/python:py_utils",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//ai_search_engine/src/python:search_engine"
    ],
    visibility = ["//visibility:public"],
)