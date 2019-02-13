py_binary(
        name="app",
        visibility = ["//visibility:public"],
        deps=[
                "//dap_api/src/protos:py_dap_api_pb",
                "//dap_api/src/python:dap_api",
                "//dap_2d_geo/src/python:dap_2d_geo",
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
        ],
        deps=[
                "//dap_api/src/python:dap_api",
        ],
)
