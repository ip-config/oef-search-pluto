py_library(
    name = "app",
    srcs = glob(["*.py"]),
    visibility = ["//visibility:public"],
    deps = [
        "//dap_2d_geo/src/python:dap_2d_geo",
        "//dap_e_r_network/src/python:dap_e_r_network",
        "//dap_api/src/python:dap_api",
        "//dap_in_memory/src/python:dap_in_memory",
        "//dap_api/experimental/python:experimental_lib",
        "//dap_api/src/protos:py_dap_api_pb",
        "//api/src/python:router_builder",
        "//utils/src/python:py_utils",
        "//api/src/python/core:utils",
        "//api/src/python:communication_handler",
        "//fake_oef/src/python/lib:lib",
        "//dap_api/experimental/python:network_dap_contract",
        "//dap_attribute_store/src/python:dap_attribute_store",
    ],
    data = [
        "//cpp_dap_in_memory/src/cpp:cpp_dap_in_memory_server",
    ],
)
