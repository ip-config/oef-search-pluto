filegroup(
    name="oef-core-orig",
    srcs = ["oef-core/build/apps/node-pluto/OEFNodePluto"]
)

genrule(
    name = "oef-core",
    srcs = [
        "//fetch_teams:oef-core",
    ],
    outs = [ "OEFNode" ],
    visibility = ["//visibility:public"],
    cmd="cp -vH $(location //fetch_teams:oef-core-orig) $@ ; echo $@ "
)
