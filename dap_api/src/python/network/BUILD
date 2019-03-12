py_library(
    name = "dap_network",
    srcs = glob(["*.py"]),
    deps = [
        "//api/src/python:serialization",
        "//api/src/python:interfaces",
        "//utils/src/python:py_utils",
        "//dap_api/src/protos:dap_api_pb",
        "//api/src/python:communication_handler",
        "//api/src/pyhon:backend_router"
    ],
    visibility = ["//visibility:public"],
)