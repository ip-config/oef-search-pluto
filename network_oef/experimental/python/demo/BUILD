py_binary(
    name="search_network",
    visibility = ["//visibility:public"],
    srcs = ["SearchNetwork.py", "main.py", "ProcessMain.py", "ContainerMain.py"],
    main="main.py",
    deps = [
        "//network_oef/experimental/python:full_node",
        "//network/src/python/async_socket:async_socket",
        "//api/src/proto/director:py_api_pb",
        "//england_grid/src/python/lib:lib",
        "//api/experimental/python:director",
        "//utils/src/python:py_utils",
    ],
    data = [
         "//crawler_demo/resources:resources",
         "//england_grid/resources/images:pop-images",
         "//fetch_teams:oef-core",
         "//cpp-sdk/experimental/resources:dap_configs",
         "//ai_search_engine/src/resources:dap_config",
         "//api/src/resources:website",
         "//docker-images:dockerfile",
    ]
)


py_binary(
    name = "demo_director",
    srcs = ["DirectorMain.py"],
    main = "DirectorMain.py",
    deps = [
        "//api/experimental/python:director",
        "//england_grid/src/python/lib:lib",
    ],
    srcs_version = "PY3",
    data = [
         "//crawler_demo/resources:resources",
         "//england_grid/resources/images:pop-images",
    ]
)