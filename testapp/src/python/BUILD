py_binary(
        name="testapp",
        visibility = ["//visibility:public"],
        deps=[
                "//fetch_teams/bottle:bottle",
                "//testapp/src/python/mainfuncs:mainfuncs",
                "//testapp/src/protos:py_testapp_pb",
                "//network/src/python/async_socket:async_socket",
                "@com_google_protobuf//:protobuf_python",
        ],
        srcs=["main/main.py"],
        main="main/main.py"
)
