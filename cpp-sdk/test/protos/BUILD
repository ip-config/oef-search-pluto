load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
    name = "testprotos_pb",
    srcs = glob(["*.proto"]),
    deps = [
         "//fetch_teams/oef_core_protocol:oef_protocol",
    ],
    visibility = [
            "//visibility:public",
    ],
)

cc_proto_library(
    name = "cc_testprotos_pb",
    visibility = [
        "//visibility:public",
    ],
    deps = [":testprotos_pb"],
)
