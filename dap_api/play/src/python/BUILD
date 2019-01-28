py_binary(
        name="app",
        visibility = ["//visibility:public"],
        deps=[
                "//dap_api/src/protos:py_dap_api_pb",
                "//dap_api/src/python:dap_api",
                "@com_google_protobuf//:protobuf_python",
        ],
        srcs=glob(["*.py"]),
        main="main.py"
)
