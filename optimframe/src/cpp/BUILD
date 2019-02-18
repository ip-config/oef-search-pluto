
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
    #copts = ["-I/opt/local/Library/Frameworks/Python.framework/Versions/3.6/include/python3.6m"],
)

cc_binary(
    name = "popgrab.so",
    visibility = [
        "//visibility:public",
    ],
    srcs = [
#        "foo.h",
    ],
    deps = [
         ":popgrab_lib"
    ],
    linkshared = True,
    linkstatic = True,
)
