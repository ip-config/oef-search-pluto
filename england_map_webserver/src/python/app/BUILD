py_binary(
    name = "app",
    srcs = ["main.py"],
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [
         "//england_map_webserver/src/python/lib:lib",
         "//pluto_app/src/python/app:app",
         "//fake_oef/src/python/lib:lib",
         "//fetch_teams/bottle:bottle",
    ],
    data = [
         "//england_grid/resources/images:pop-images",
    ]
)
