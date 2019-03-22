py_library(
    name = "app",
    srcs = glob(["*.py"]),
    visibility = ["//visibility:public"],
    deps = [
        "//dap_2d_geo/src/python:dap_2d_geo",
        "//dap_e_r_network/src/python:dap_e_r_network",
        "//dap_api/src/python:dap_api",
        "//dap_api/experimental/python:experimental_lib",
        "//dap_api/src/protos:py_dap_api_pb",
        "//api/src/python:backend_router",
        "//api/src/python:endpoints",
        "//utils/src/python:py_utils",
        "//api/src/python:utils",
        "//api/src/python:communication_handler",
        "//fake_oef/src/python/lib:lib",
        "//dap_api/experimental/python:network_dap_contract"
    ],
)
