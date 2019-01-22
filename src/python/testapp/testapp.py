#!/usr/bin/env python

from src.python.testapp.mainfuncs import say_hello
from src.protos.testapp import a_pb2

def main():
    msg = say_hello.say_hello()
    print("MSG={}".format(repr(msg)))
    result = a_pb2.A()
    result.ParseFromString(msg)
    print(result.data)

if __name__ == "__main__":
    main()

