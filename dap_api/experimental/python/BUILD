py_binary(
        name="app",
        visibility = ["//visibility:public"],
        deps=[
                "//dap_api/src/protos:py_dap_api_pb",
                "//dap_api/src/python:dap_api",
                "@com_google_protobuf//:protobuf_python",
                ":experimental_lib"
        ],
        srcs=["main.py"],
        main="main.py",
)

py_library(
        name="experimental_lib",
        visibility = ["//visibility:public"],
        srcs=[
                "InMemoryDap.py",
                "AddressRegistry.py"
        ],
        deps=[
                "//dap_api/src/protos:py_dap_api_pb",
                "//dap_api/src/python:dap_api",
                "@com_google_protobuf//:protobuf_python",
                "//utils/src/python:py_utils"
        ],
)
