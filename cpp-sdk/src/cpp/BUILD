cc_library(
    name = "lib",
    visibility = [
        "//visibility:public",
    ],
    srcs = [
        "Listner.cpp"
    ],
    hdrs = [
         "Transport.hpp",
         "DapInterface.hpp",
         "Listener.hpp"
         ],
    deps = [
        "@boost//:asio",
        "@boost//:coroutine2"
    ],
)

cc_binary(
    name = "server",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["main.cpp"]),
    deps = [
        ":lib",
    ],
    #linkshared = True,
    #linkstatic = True,
)

