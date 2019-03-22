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
        srcs = [ x for x in glob(["*.py"]) if x[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" ],
        deps=[
                "//dap_api/src/protos:py_dap_api_pb",
                "//dap_api/src/python:dap_api",
                "@com_google_protobuf//:protobuf_python",
                "//utils/src/python:py_utils",
                "//dap_api/src/python/network:dap_network"
        ],
)

py_library(
    name="network_dap_contract",
    visibility = ["//visibility:public"],
    srcs = ["NetworkDapContract.py"]
)

py_binary(
    name="network_daps",
    visibility = ["//visibility:public"],
    srcs = ["RunNetworkDaps.py"],
    main="RunNetworkDaps.py",
    deps=[
        ":experimental_lib",
        ":network_dap_contract",
        "//ai_search_engine/src/python:search_engine",
    ]

)