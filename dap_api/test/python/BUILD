py_library(
    name = "mocks",
    srcs = glob(["*Mock.py"]),
    deps = [
        "//dap_api/src/python:dap_api",
        "//dap_api/src/protos:py_dap_api_pb",
    ],
)

py_library(
    name = "classes",
    srcs = glob(["*Test.py"]),
    deps = [
        "//dap_api/src/python:dap_api",
        "//dap_api/src/protos:py_dap_api_pb",
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
        "//dap_api/experimental/python:experimental_lib",
        "//dap_api/src/protos:py_dap_api_pb",
        ":mocks",
        ":classes",
    ]
)
