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