load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
    name = "director_api_pb",
    srcs = glob(["*.proto"]),
    deps = ["//fetch_teams/oef_core_protocol:oef_protocol"]

)

py_proto_library(
    name = "py_director_api_pb",
    srcs = glob(["*.proto"]),
    protoc = "@com_google_protobuf//:protoc",
    default_runtime = "@com_google_protobuf//:protobuf_python",
    visibility = ["//visibility:public"],
    deps = ["//fetch_teams/oef_core_protocol:py_oef_protocol"]
)

cc_proto_library(
    name = "cc_director_api_pb",
    visibility = [
        "//visibility:public",
    ],
    deps = [":api_pb"],
)
