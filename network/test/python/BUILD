py_binary(
    name = "test_server",
    srcs = ["EchoServer.py"],
    main = "EchoServer.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/proto:py_api_pb"
    ],
    srcs_version = "PY3",
)

py_binary(
    name = "test_client",
    srcs = ["Client.py"],
    main = "Client.py",
    deps = ["//network/src/python/async_socket:async_socket"],
    srcs_version = "PY3",
)

