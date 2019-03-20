load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
    name = "dap_config_pb",
    srcs = glob(["*.proto"]),
    deps = ["//dap_api/src/protos:dap_api_pb"]
)


cc_proto_library(
    name = "cc_dap_config_pb",
    visibility = [
        "//visibility:public",
    ],
    deps = [":dap_config_pb"],
)
