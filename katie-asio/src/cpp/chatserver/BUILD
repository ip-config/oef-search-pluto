cc_binary(
    name = "chatserver",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["commserver.cpp"]),
    deps = [
        "//katie-asio/src/cpp/comms:lib",
        ":lib",
    ],
    #linkshared = True,
    #linkstatic = True,
)

cc_library(
    name = "lib",
    visibility = [
        "//visibility:public",
    ],
    srcs = [
         "ChatClient.cpp",
         "ChatCore.cpp",
    ],
    hdrs = [
         "Oink.hpp",
         "ChatClient.hpp",
         "ChatCore.hpp",
         ],
    deps = [
        "@boost//:asio",
        "//katie-asio/src/cpp/comms:lib",
    ],
)

