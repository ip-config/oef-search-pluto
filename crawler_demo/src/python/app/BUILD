py_binary(
    name = "crawler_demo",
    srcs = ["main.py"],
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [
         "//england_grid/src/python/lib:lib",
         "//crawler_demo/src/python/lib:lib",
         "//behaviour_tree/src/python/lib:lib",
         "//utils/src/python:py_utils",
         "//api/src/proto:py_api_pb",
    ],
    data = [
         "//crawler_demo/resources:resources",
         "//england_grid/resources/images:pop-images",
    ]
)
