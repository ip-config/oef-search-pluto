cc_binary(
    name = "app",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["main.cpp"]),
    deps = [
        ":lib",
        "//katie-pb/src/protos:cc_katie_pb",
    ],
    #linkshared = True,
    #linkstatic = True,
)

cc_library(
    name = "lib",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["*.cpp"]),
    hdrs = glob(["*.hpp"]),
    deps = [
        "@boost//:asio",
        "//katie-pb/src/protos:cc_katie_pb",
    ],
)

