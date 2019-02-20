cc_library(
    name = "popgrab_lib",
    visibility = [
        "//visibility:public",
    ],
    srcs = [
        "popgrab_module.cpp",
    ],
    deps = [
         "@python_headers//:headers",
    ],
    hdrs = ["PopulationGrabber.hpp"],
)

cc_binary(
    name = "popgrab.so",
    visibility = [
        "//visibility:public",
    ],
    srcs = [
    ],
    deps = [
         ":popgrab_lib"
    ],
    linkshared = True,
    linkstatic = True,
)
