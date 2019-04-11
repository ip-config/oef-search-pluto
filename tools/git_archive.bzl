FINDER="""
#!/usr/bin/env python3

import sys
import os
import re
import glob
import subprocess


def main():
    source_dir = "{}"
    output = os.getcwd()
    print('Generating source archive...')
    cmd = [
        'git-archive-all', os.path.join(output, 'project.tar.gz')
    ]
    subprocess.check_call(cmd, cwd=source_dir)
    print('Generating source archive...complete')

if __name__ == '__main__':
    main()
"""


def project_tar_gz(repository_ctx):
    repository_ctx.file("FINDER", content=FINDER.format(repository_ctx.attr.path))
    r = repository_ctx.execute(["python3", "./FINDER", repository_ctx.attr.path], timeout=15)
    print(r.stdout)
    if len(r.stderr) > 0:
        print(r.stderr)
    repository_ctx.file("BUILD", content="""
package(
    default_visibility = [
        "//visibility:public",
    ],
)

filegroup(
    name = "project_tar_gz",
    srcs = glob(["**/*.tar.gz"]),
)
""", executable=True)


project_tar_gz_repository = repository_rule(
    implementation=project_tar_gz,
    attrs = {
        "path": attr.string(mandatory=True)
    }
)
