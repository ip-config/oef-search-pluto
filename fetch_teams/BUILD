filegroup(
    name="oef-core-orig",
    srcs = ["oef-core-pluto/build/apps/node-pluto/OEFNodePluto"]
)

genrule(
    name = "oef-core",
    srcs = [
        "//fetch_teams:oef-core-orig",
    ],
    outs = [ "OEFNode" ],
    visibility = ["//visibility:public"],
    cmd="cp -vH $(location //fetch_teams:oef-core-orig) $@ ; echo $@ "
)
