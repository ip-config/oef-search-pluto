py_library(
    name = "mocks",
    srcs = glob(["*Mock.py"]),
    deps = [
    ],
)

py_library(
    name = "classes",
    srcs = glob(["*Test.py"]),
    deps = [
         "//fake_oef/src/python/lib:lib",
    ],
)

py_test(
    name = "tests",
    main = "tests.py",
    srcs = [
         "tests.py",
    ],
    data = [
    ],
    deps = [
        ":classes",
    ]
)
