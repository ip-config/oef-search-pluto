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
         "//toby_loader/data/csv:tobydata",
         "//optimframe/src/data:popdata",
         "//optimframe/src/python/lib:lib",
         "//fetch_teams/bottle:bottle",
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
