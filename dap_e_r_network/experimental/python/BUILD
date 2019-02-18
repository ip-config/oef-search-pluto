py_binary(
        name="app",
        visibility = ["//visibility:public"],
        deps=[
                "//pluto_app/src/python/app:app",
                "//dap_api/src/python:dap_api",
                "//dap_e_r_network/src/python:dap_e_r_network",
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
                "//dap_e_r_network/src/python:dap_e_r_network",
        ],
)
