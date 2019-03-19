load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "com_google_protobuf",
    sha256 = "9510dd2afc29e7245e9e884336f848c8a6600a14ae726adb6befdb4f786f0be2",
    strip_prefix = "protobuf-3.6.1.3",
    urls = ["https://github.com/google/protobuf/archive/v3.6.1.3.zip"],
)

http_archive(
    name = "six_archive",
    build_file = "@//:six.BUILD",
    sha256 = "105f8d68616f8248e24bf0e9372ef04d3cc10104f1980f54d57b2ce73a5ad56a",
    urls = ["https://pypi.python.org/packages/source/s/six/six-1.10.0.tar.gz#md5=34eed507548117b2ab523ab14b2f8b55"],
)

bind(
  name = "six",
  actual = "@six_archive//:six",
)

http_archive(
    name = "bazel_skylib",
    sha256 = "bbccf674aa441c266df9894182d80de104cabd19be98be002f6d478aaa31574d",
    strip_prefix = "bazel-skylib-2169ae1c374aab4a09aa90e65efe1a3aad4e279b",
    urls = ["https://github.com/bazelbuild/bazel-skylib/archive/2169ae1c374aab4a09aa90e65efe1a3aad4e279b.tar.gz"],
)

http_archive(
    name = "pypi_six",
    url = "https://pypi.python.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz",
    build_file_content = """
py_library(
    name = "six",
    srcs = ["six.py"],
    visibility = ["//visibility:public"],
)
    """,
    strip_prefix = "six-1.11.0",
)

http_archive(
    name = "protobuf_python",
    url = "https://files.pythonhosted.org/packages/1b/90/f531329e628ff34aee79b0b9523196eb7b5b6b398f112bb0c03b24ab1973/protobuf-3.6.1.tar.gz",
    build_file_content = """
py_library(
    name = "protobuf_python",
    srcs = glob(["google/protobuf/**/*.py"]),
    visibility = ["//visibility:public"],
    imports = [
        "@pypi_six//:six",
    ],
)
    """,
    strip_prefix = "protobuf-3.6.1",
)


## proto_library, cc_proto_library, and java_proto_library rules implicitly
## depend on @com_google_protobuf for protoc and proto runtimes.
## This statement defines the @com_google_protobuf repo.
#http_archive(
#    name = "com_google_protobuf",
#    sha256 = "7b28271a61a3da0a37f6fda399b0c4c86464e5b3",
#    strip_prefix = "protobuf-3.6.1.1",
#    urls = ["https://github.com/google/protobuf/archive/v3.6.1.1.zip"],
#    visibility = ["//visibility:public"]
#)


# This is the original of the python getter replaced by the new repo rule.
#
#new_local_repository(
#    name = "python_headers",
#    path = find_python(), #"/opt/local/Library/Frameworks/Python.framework/Versions/3.6/include/python3.6m",
#    build_file_content = """
#package(
#    default_visibility = [
#        "//visibility:public",
#    ],
#)
#cc_library(
#    name = "headers",
#    srcs = glob(["**/*.h"]),
#)
#""",
#)

load("//tools:find_python.bzl", "new_system_python_headers_repository")
new_system_python_headers_repository(
        name="python_headers",
)
