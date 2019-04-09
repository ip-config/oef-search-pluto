#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import argparse

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCKER_DIR_PATH = os.path.abspath(os.path.dirname(__file__))


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="oef-search-node", type=str, required=False, help="Docker image name")
    parser.add_argument('-f', '--force', dest='force_build', action='store_true', help='Force docker image build')
    return parser.parse_args()


def check_project_path():
    tests = [
        os.path.isdir(PROJECT_PATH),
        os.path.isdir(os.path.join(PROJECT_PATH, 'docker-images')),
        os.path.isfile(os.path.join(PROJECT_PATH, 'BUILD')),
        os.path.isfile(os.path.join(PROJECT_PATH, 'WORKSPACE')),
    ]

    if not all(tests):
        raise RuntimeError('Failed to detect project layout')


def get_project_version():
    return subprocess.check_output(['git', 'describe', '--dirty=-wip', '--always'], cwd=PROJECT_PATH).decode().strip()


def main():
    args = parse_commandline()

    # auto detect the projec path
    check_project_path()

    version = get_project_version()

    if not args.force_build and version.endswith('-wip'):
        print('Unable to build image from versions with un-commited changes: ', version)
        sys.exit(1)

    # based on the version generate the required tags
    latest_docker_tag = args.name+':latest'

    print('Generating source archive...')
    cmd = [
        'git-archive-all', os.path.join(DOCKER_DIR_PATH, 'project.tar.gz')
    ]
    subprocess.check_call(cmd, cwd=PROJECT_PATH)
    print('Generating source archive...complete')

    print('Building constellation image...')
    cmd = [
        'docker',
        'build',
        '-t', latest_docker_tag,
        '.',
    ]
    subprocess.check_call(cmd, cwd=DOCKER_DIR_PATH)


if __name__ == '__main__':
    main()
