py_library(
    name = "endpoints",
    srcs = glob(["*Endpoint.py"]),
    deps = [
        "//api/src/python:serialization",
        "//api/src/python:interfaces",
        "//api/src/proto/director:py_api_pb",
        "//utils/src/python:py_utils",
        "//dap_api/src/protos:py_dap_api_pb",
        "//dap_api/src/python:dap_api"
    ],
    visibility = ["//visibility:public"],

)