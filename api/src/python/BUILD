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
        "//api/src/proto:py_api_pb",
        "//utils/src/python:py_utils",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
        "//ai_search_engine/src/python:search_engine"
    ],
)

py_library(
    name = "backend_router",
    srcs = ["BackendRouter.py"],
    deps = [
        "//api/src/python:interfaces",
        "//api/src/python:serialization",
        "//utils/src/python:py_utils"
    ],
)

py_library(
    name = "utils",
    srcs = ["ProtoWrappers.py"],
    deps = [
        "//dap_api/src/python:dap_api",
        "//api/src/proto:py_api_pb",
        "//fetch_teams/oef_core_protocol:py_oef_protocol",
    ]
)

py_binary(
    name = "communication_handler",
    srcs = ["CommunicationHandler.py"],
    main = "CommunicationHandler.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/python:backend_router",
        "//api/src/python:endpoints",
        "//fetch_teams/bottle:bottle",
        "//utils/src/python:py_utils",
        "//ai_search_engine/src/python:search_engine",
        "//dap_api/src/python:dap_api",
        ":utils"
    ],
    srcs_version = "PY3",
)
