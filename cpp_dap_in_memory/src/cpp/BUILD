cc_library(
    name = "cpp_dap_in_memory",
    visibility = [
        "//visibility:public",
    ],
    srcs = [ x for x in glob(["*.cpp"]) if x[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" ],
    hdrs = [ x for x in glob(["*.hpp"]) if x[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" ],
    deps = [
         "//cpp-sdk/src/cpp:lib",
         "//cpp_dap_utils/src/cpp:cpp_dap_utils",
         "//cpp-sdk/experimental/protos:cc_dap_config_pb",
    ],
)

cc_binary(
    name = "cpp_dap_in_memory_server",
    visibility = [
        "//visibility:public",
    ],
    srcs = [ "main.cpp" ],
    deps = [
         ":cpp_dap_in_memory",
         "//cpp-sdk/src/cpp:lib",
         "//cpp_dap_utils/src/cpp:cpp_dap_utils",
         "//cpp-sdk/experimental/protos:cc_dap_config_pb",
         "@boost//:program_options",
    ],
    
)