py_library(
    name = "serialization",
    srcs = ["Serialization.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "interfaces",
    srcs = glob(["Interface*.py"]),
    visibility = ["//visibility:public"],
)

py_library(
    name = "backend_router",
    srcs = ["BackendRouter.py"],
    deps = [
        "//api/src/python:interfaces",
        "//api/src/python:serialization",
        "//utils/src/python:py_utils"
    ],
    visibility = ["//visibility:public"],
)

py_library(
    name = "communication_handler",
    srcs = ["CommunicationHandler.py"],
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/python:backend_router",
        "//fetch_teams/bottle:bottle",
        "//utils/src/python:py_utils",
        "//api/src/python/core:utils",
    ],
    data = [
        "//api/src/resources:website"
    ],
    srcs_version = "PY3",
    visibility = ["//visibility:public"],
)
