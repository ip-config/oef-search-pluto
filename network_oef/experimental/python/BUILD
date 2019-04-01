py_binary(
    name="node",
    visibility = ["//visibility:public"],
    srcs = ["FullNode.py"],
    main="FullNode.py",
    deps=[
        "//network_oef/src/python:lib",
        "//utils/src/python:py_utils",
    ],
    data = [
            "//cpp-sdk/experimental/resources:dap_configs",
            "//ai_search_engine/src/resources:dap_config",
            "//api/src/resources:website",
            "//fetch_teams:oef-core",
    ]
)
