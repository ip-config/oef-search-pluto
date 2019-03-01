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
         "//utils/src/python:py_utils",
         "//fetch_teams/bottle:bottle",
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
