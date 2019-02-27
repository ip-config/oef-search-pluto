py_binary(
    name = "main",
    srcs = ["main.py"],
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [
         "//optimframe/src/python/openpopgrid:openpopgrid",
         "//optimframe/src/python/node:self_org_node",
         "//optimframe/src/python/lib:lib",
    ]
)
py_binary(
    name = "main_sa",
    srcs = ["main_sa.py"],
    main = "main_sa.py",
    visibility = ["//visibility:public"],
    deps = [
         "//optimframe/src/python/openpopgrid:openpopgrid",
         "//optimframe/src/python/node:self_org_node",
         "//optimframe/src/python/lib:lib",
    ],
    data = [
        "//toby_loader/data/csv:cities"
    ]
)

py_binary(
    name = "main_dqn",
    srcs = ["main_dqn.py"],
    main = "main_dqn.py",
    visibility = ["//visibility:public"],
    deps = [
         "//optimframe/src/python/openpopgrid:openpopgrid",
         "//optimframe/src/python/node:self_org_node",
         "//optimframe/src/python/lib:lib",
    ],
    data = [
        "//toby_loader/data/csv:cities"
    ]
)


py_binary(
    name = "fenv_dqn",
    srcs = ["fenv_dqn.py"],
    main = "fenv_dqn.py",
    visibility = ["//visibility:public"],
    deps = [
         "//optimframe/src/python/openpopgrid:openpopgrid",
         "//optimframe/src/python/node:self_org_node",
         "//optimframe/src/python/lib:lib",
    ],
    data = [
        "//toby_loader/data/csv:cities"
    ]
)
