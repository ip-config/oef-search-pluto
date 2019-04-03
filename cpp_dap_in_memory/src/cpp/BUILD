cc_library(
    name = "cpp_dap_in_memory",
    visibility = [
        "//visibility:public",
    ],
    srcs = glob(["*.cpp"]),
    hdrs = glob(["*.hpp"]),
    deps = [
         "//cpp-sdk/src/cpp:lib",
         "//cpp_dap_utils/src/cpp:cpp_dap_utils",
         "//cpp-sdk/experimental/protos:cc_dap_config_pb"
    ],
)
