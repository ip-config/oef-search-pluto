filegroup(
    name="dockerfile",
    visibility=["//visibility:public"],
    srcs=[
        "Dockerfile",
    ],
    data=[
        "project.tar.gz"
    ]
)

genrule(
    name = "project_source",
    srcs = [
        "@git_project//:project_tar_gz"
    ],
    outs = ["project.tar.gz"],
    cmd="cp -vH $(location @git_project//:project_tar_gz) $@ && echo $@"

)
