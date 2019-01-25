py_library(
    name = "backend_entry_point",
    srcs = ["BackendEntryPoint.py"],
    deps = [
        "//api/src/proto:py_api_pb"
    ],
)

py_binary(
    name = "communication_handler",
    srcs = ["CommunicationHandler.py"],
    main = "CommunicationHandler.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto:py_api_pb",
        "//api/src/python:backend_entry_point",
        "//third_party/bottle:bottle",
    ],
    srcs_version = "PY3",
)
