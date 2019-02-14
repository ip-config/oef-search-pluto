
#py_library(
#    name = "mocks",
#    srcs = glob(["*Mock.py"]),
#    deps = [
#        "//dap_e_r_network/src/python:dap_e_r_network",
#        "//dap_e_r_network/src/protos:py_dap_e_r_network_pb",
#    ],
#)

py_library(
    name = "classes",
    srcs = glob(["*Test.py"]),
    deps = [
        "//dap_e_r_network/src/python:dap_e_r_network",
    ],
)

py_test(
    name = "tests",
    main = "tests.py",
    srcs = [
         "tests.py",
    ],
    deps = [
        "//dap_api/src/python:dap_api",
        "//dap_e_r_network/src/python:dap_e_r_network",
        "//ai_search_engine/src/python:search_engine",
        ":classes",
    ]
)
