py_library(
    name = "dap_network",
    srcs = glob(["*.py"]),
    deps = [
        "//api/src/python:serialization",
        "//api/src/python:interfaces",
        "//utils/src/python:py_utils",
        "//dap_api/src/protos:py_dap_api_pb",
        "//api/src/python:communication_handler",
        "//api/src/python:backend_router",
        "//network/src/proto:py_network_pb",
    ],
    visibility = ["//visibility:public"],
)