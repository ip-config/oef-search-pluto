load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
    name = "testapp_pb",
    srcs = ["a.proto"],
)

py_proto_library(
    name = "py_testapp_pb",
    srcs = ["a.proto"],
    protoc = "@com_google_protobuf//:protoc",
    default_runtime = "@com_google_protobuf//:protobuf_python",
    visibility = ["//visibility:public"],
)
