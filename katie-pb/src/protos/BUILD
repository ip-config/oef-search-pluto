load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
    name = "katie_pb",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["*.proto"]),
    deps = []
)

cc_proto_library(
    name = "cc_katie_pb",
    visibility = [
        "//visibility:public",
    ],
    deps = [":katie_pb"],
)
