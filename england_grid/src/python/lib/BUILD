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
