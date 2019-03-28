py_binary(
    name="node_test",
    visibility = ["//visibility:public"],
    srcs = ["TestNode.py"],
    main="TestNode.py",
    deps=[
        "//network_oef/src/python:lib"
    ],
    data = [
            "//cpp-sdk/experimental/resources:dap_configs",
            "//ai_search_engine/src/resources:dap_config",
            "//api/src/resources:website"
    ]
)
