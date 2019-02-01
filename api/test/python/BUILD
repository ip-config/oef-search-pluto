py_binary(
    name = "communication_handler",
    srcs = ["CommunicationHandler.py"],
    main = "CommunicationHandler.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto:py_api_pb"
    ],
    srcs_version = "PY3",
)

py_binary(
    name = "register_agents",
    srcs = ["RegisterAgents.py"],
    main = "RegisterAgents.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto:py_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
    ],
    srcs_version = "PY3",
)
