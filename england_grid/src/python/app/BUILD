py_binary(
    name = "england_grid",
    srcs = ["main.py"],
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [
         "//england_grid/src/python/lib:lib",
    ],
    data = [
         "popgrab.so",
         "//england_grid/resources/images:pop-images",
    ]
)

# Shouldn't be needed...

genrule(
    name = "copy_popgrab_shared_obj",
    srcs = [
        "//optimframe/src/cpp:popgrab.so",
    ],
    outs = [ "popgrab.so" ],

    cmd="cp -vH $(location //optimframe/src/cpp:popgrab.so) $@"
)
