load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
    name = "network_pb",
    srcs = glob(["*.proto"]),
)

py_proto_library(
    name = "py_network_pb",
    srcs = glob(["*.proto"]),
    protoc = "@com_google_protobuf//:protoc",
    default_runtime = "@com_google_protobuf//:protobuf_python",
    visibility = ["//visibility:public"],
    deps = [
    ]
)

cc_proto_library(
    name = "cc_network_pb",
    visibility = [
        "//visibility:public",
    ],
    deps = [":network_pb"],
)
