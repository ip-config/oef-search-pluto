py_library(
    name="lib",
    visibility = ["//visibility:public"],
    srcs = glob(["*.py"]),
    deps = [
        "//optimframe/src/python/openpopgrid:openpopgrid",
    ],
    data = [
         "popgrab.so",
         "//dap_2d_geo/test/resources:airports",
         "//fetch_teams/bottle:bottle",
         "//optimframe/src/data:popdata",
         "//optimframe/src/python/lib:lib",
         "//svg_output/src/python/lib:lib",
         "//toby_loader/data/csv:cities",
         "//fake_oef/src/python/lib:lib",
         "//utils/src/python:py_utils",
         "//api/src/python/core:utils",
         "//api/src/python:communication_handler",
         "//api/src/proto/core:py_api_pb",
         "//pluto_app/src/python/app:app",
         "//fetch_teams/oef_core_protocol:py_oef_protocol",
    ],
)

genrule(
    name = "copy_popgrab_shared_obj",
    srcs = [
        "//optimframe/src/cpp:popgrab.so",
    ],
    outs = [ "popgrab.so" ],

    cmd="cp -vH $(location //optimframe/src/cpp:popgrab.so) $@"
)
