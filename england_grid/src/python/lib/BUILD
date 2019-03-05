py_library(
    name="lib",
    visibility = ["//visibility:public"],
    srcs = glob(["*.py"]),
    deps = [
        "//optimframe/src/python/openpopgrid:openpopgrid",
         "//fetch_teams/bottle:bottle",
         "//optimframe/src/python/lib:lib",
         "//svg_output/src/python/lib:lib",
    ],
    data = [
         "//dap_2d_geo/test/resources:airports",
         "//toby_loader/data/csv:cities",
         "//optimframe/src/data:popdata",
         "popgrab.so",
    ],
)

genrule(
    name = "copy_popgrab_shared_obj",
    srcs = [
        "//optimframe/src/cpp:popgrab.so",
    ],
    outs = [ "popgrab.so" ],

    cmd="cp -vH $(location //optimframe/src/cpp:popgrab.so) $@ ; echo $@ "
)
