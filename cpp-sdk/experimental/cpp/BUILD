cc_library(
    name = "daps",
    visibility = [
        "//visibility:public",
    ],
    srcs = [
    ],
    hdrs = glob(["*.hpp"]),
    deps = [
        "//cpp-sdk/src/cpp:lib",
        "//cpp-sdk/experimental/protos:cc_dap_config_pb"
    ],
)

cc_binary(
    name = "server",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["*.cpp"]),
    deps = [
        ":daps",
        "//cpp-sdk/src/cpp:lib",
    ],
    data = [
        "//cpp-sdk/experimental/resources:dap_configs"
    ]
    #linkshared = True,
    #linkstatic = True,
)

