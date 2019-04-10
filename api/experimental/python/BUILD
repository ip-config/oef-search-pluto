py_binary(
    name = "demo_director",
    srcs = ["Director.py", "DemoDirector.py"],
    main = "DemoDirector.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/director:py_api_pb",
        "//england_grid/src/python/lib:lib",
    ],
    srcs_version = "PY3",
    data = [
         "//crawler_demo/resources:resources",
         "//england_grid/resources/images:pop-images",
    ]
)

py_library(
    name = "director",
    srcs = ["Director.py", "DemoWeatherAgent.py"],
    visibility = ["//visibility:public"],
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/director:py_api_pb",
        "//api/src/proto/core:py_api_pb",

    ],
    srcs_version = "PY3",
)

py_binary(
    name = "demo_agents",
    srcs = ["Director.py", "DemoWeatherAgent.py"],
    main = "DemoWeatherAgent.py",
    deps = [
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/director:py_api_pb",
        "//api/src/proto/core:py_api_pb",

    ],
    srcs_version = "PY3",

)