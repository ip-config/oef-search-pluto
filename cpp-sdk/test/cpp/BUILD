cc_test(
    name = "tests",
    srcs = glob(["**/*.cpp"]),
    deps = [
         "@googletest//:gtest_main",
         "@boost//:asio",
         "//cpp-sdk/src/cpp:lib",
         "//cpp-sdk/test/protos:cc_testprotos_pb",
    ],
)
