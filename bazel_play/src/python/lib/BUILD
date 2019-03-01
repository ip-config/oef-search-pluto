py_library(
    name="lib",
    visibility = ["//visibility:public"],
    srcs = glob(["*.py"]),
    deps = [
    ],
    data = [
         "foo.txt",
         "popgrab.so",
    ],
)


genrule(
    name = "make_foo_textfile",
    srcs = [
    ],
    outs = [ "foo.txt" ],

    cmd="echo 'wabble' > $@"
)


genrule(
    name = "copy_popgrab_shared_obj",
    srcs = [
        "//optimframe/src/cpp:popgrab.so",
    ],
    outs = [ "popgrab.so" ],

    cmd="cp -vH $(location //optimframe/src/cpp:popgrab.so) $@"
)
