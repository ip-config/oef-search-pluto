import os
import sys

from utils.src.python import resources

def main():
    print(resources.textlines('bazel_play/src/python/lib/foo.txt'))

if __name__ == '__main__':
    main()
