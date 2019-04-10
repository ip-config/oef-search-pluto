py_binary(
    name = "crawler_demo",
    srcs = ["main.py"],
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [
         "//fake_oef/src/python/lib:lib",
         "//england_grid/src/python/lib:lib",
         "//crawler_demo/src/python/lib:lib",
         "//behaviour_tree/src/python/lib:lib",
         "//utils/src/python:py_utils",
         "//pluto_app/src/python/app:app",
         "//api/src/proto/core:py_api_pb",
         "//fetch_teams/bottle:bottle",
    ],
    data = [
         "//crawler_demo/resources:resources",
         "//england_grid/resources/images:pop-images",
    ]
)

