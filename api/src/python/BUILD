py_library(
    name = "serialization",
    srcs = ["Serialization.py"],
)

py_library(
    name = "interfaces",
    srcs = glob(["Interface*.py"]),
)

py_library(
    name = "endpoints",
    srcs = glob(["Endpoint*.py"]),
    deps = [
        "//api/src/python:serialization",
        "//api/src/python:interfaces",
        "//api/src/proto:py_api_pb"
    ],
)

py_library(
    name = "backend_router",
    srcs = ["BackendRouter.py"],
    deps = [
        "//api/src/python:interfaces",
        "//api/src/python:serialization"
    ],
)

py_binary(
    name = "communication_handler",
    srcs = ["CommunicationHandler.py"],
    main = "CommunicationHandler.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/python:backend_router",
        "//api/src/python:endpoints",
        "//third_party/bottle:bottle",
    ],
    srcs_version = "PY3",
)
