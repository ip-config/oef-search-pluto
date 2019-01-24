py_binary(
        name="testapp",
        visibility = ["//visibility:public"],
        deps=[
                "//third_party/bottle:bottle",
                "//testapp/src/python/mainfuncs:mainfuncs",
                "//testapp/src/protos:py_testapp_pb",
        ],
        srcs=["main/main.py"],
        main="main/main.py"
)
