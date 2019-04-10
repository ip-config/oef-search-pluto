py_library(
    name="crawler_lib",
    visibility = ["//visibility:public"],
    srcs = [
        "CrawlerAgent.py",
        "CrawlerAgentBehaviour.py",
        "CrawlerAgents.py",
    ],
    deps = [
    ],
    data = [
         "//utils/src/python:py_utils",
    ],
)

py_library(
    name="fake_lib",
    visibility = ["//visibility:public"],
    srcs = [
         "SearchNetwork.py",
    ],
    deps = [
    ],
    data = [
         "//utils/src/python:py_utils",
    ],
)

#         "//api/src/python/core:utils",
#        "//optimframe/src/python/openpopgrid:openpopgrid",
#         "//svg_output/src/python/lib:lib",
#         "//pluto_app/src/python/app:app",
#         "//dap_2d_geo/test/resources:airports",
#         "//fetch_teams/bottle:bottle",
#         "//optimframe/src/data:popdata",
#         "//optimframe/src/python/lib:lib",
#         "//toby_loader/data/csv:cities",
#         "popgrab.so",

genrule(
    name = "copy_popgrab_shared_obj",
    srcs = [
        "//optimframe/src/cpp:popgrab.so",
    ],
    outs = [ "popgrab.so" ],

    cmd="cp -vH $(location //optimframe/src/cpp:popgrab.so) $@"
)
