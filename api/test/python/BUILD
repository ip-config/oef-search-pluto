py_binary(
    name = "communication_handler",
    srcs = ["CommunicationHandler.py"],
    main = "CommunicationHandler.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/core:py_api_pb"
    ],
    srcs_version = "PY3",
)

py_binary(
    name = "register_oefs",
    srcs = ["RegisterOEFs.py"],
    main = "RegisterOEFs.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/core:py_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
    ],
    srcs_version = "PY3",
)

py_binary(
    name = "remove_oefs",
    srcs = ["RemoveOEFs.py"],
    main = "RemoveOEFs.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/core:py_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
    ],
    srcs_version = "PY3",
)