FINDER="""
#!/usr/bin/env python3

import sys
import os
import re
import glob

INCL = re.compile(r'#include\s+"([^"]+)"')

def num(s):
    try:
        return float(s)
    except ValueError:
        return None

def find_python():
    POSSIBLE_PYTHON_SOURCE_VERSION_LOCATIONS=[
        ("/opt/local/Library/Frameworks/Python.framework/Versions/"),
        ("/usr/local/Frameworks/Python.framework/Versions/"),
    ]

    versions = []
    for p in POSSIBLE_PYTHON_SOURCE_VERSION_LOCATIONS:
        if not os.path.exists(p):
            continue
        dirs = os.listdir(p)
        versions.extend([
            (v, d, p)
            for v, d, p in
            [ (num(d), d, p) for d in dirs ]
            if v != None
        ])

    locations = []
    for v, d, p in versions:
        locations.extend([
            (v, d, p, os.path.dirname(h).replace(p +  d + "/", ""))
            for h
            in glob.glob(p +  d + "/include/*/Python.h")
        ])
    best = sorted(locations, key=lambda x: x[0], reverse=True)[0]

    return best[2]+best[1]+"/"+best[3]

def create_file_list(fn, path, files_processed):
    path_fn = os.path.join(path, fn)
    with open(path_fn, "r") as fh:
        lines = fh.readlines()
    newfiles = set()

    matches = [
        x for x in
        [ re.match(INCL, line.strip()) for line in lines ]
        if x
    ]
    if matches:
        includes = set([ m.groups()[0] for m in matches if m ])
        new_includes = includes - files_processed
        files_processed |= new_includes
        for n in new_includes:
            files_processed |= create_file_list(n, path, files_processed)
    return files_processed

def main():
    original = find_python()
    output = os.getcwd()
    r = create_file_list(
        "Python.h",
        original,
        set([ os.path.basename("Python.h") ]))

    for fn in r:
        src = os.path.join(original, fn)
        dst = os.path.join(output, fn)
        os.symlink(src, dst)

if __name__ == '__main__':
    main()
"""


def python_system_headers_repository(repository_ctx):
    repository_ctx.file("FINDER", content=FINDER)
    r = repository_ctx.execute(["python3", "./FINDER"], timeout=15)
    print(r.stdout)
    repository_ctx.file("BUILD", content="""
package(
    default_visibility = [
        "//visibility:public",
    ],
)

cc_library(
    name = "headers",
    srcs = glob(["**/*.h"]),
)
""", executable=True)


new_system_python_headers_repository = repository_rule(
    implementation=python_system_headers_repository,
    attrs = {
    }
)