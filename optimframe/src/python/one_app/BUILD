py_binary(
    name = "one",
    srcs = ["one.py"],
    main = "one.py",
    visibility = ["//visibility:public"],
    deps = [
         "//optimframe/src/python/openpopgrid:openpopgrid",
    ],
    data = [
#         "//optimframe/src/cpp:popgrab.so",
#         "//bazel-bin/optimframe/src/cpp/popgrab.so"
         "popgrab.so"
    ],
)
