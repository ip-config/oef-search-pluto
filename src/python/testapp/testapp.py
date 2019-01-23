#!/usr/bin/env python

import functools
import os
import threading
import sys

from src.protos.testapp import a_pb2
from src.python.testapp.mainfuncs import say_hello
from src.third_party.bottle import SSLWSGIRefServer
from src.third_party.bottle.bottle import abort
from src.third_party.bottle.bottle import Bottle
from src.third_party.bottle.bottle import error
from src.third_party.bottle.bottle import hook
from src.third_party.bottle.bottle import redirect
from src.third_party.bottle.bottle import request
from src.third_party.bottle.bottle import response
from src.third_party.bottle.bottle import route
from src.third_party.bottle.bottle import run
from src.third_party.bottle.bottle import static_file
from src.third_party.bottle.bottle import template

# Build me like this:
#   bazel build src/python/testapp:testapp
#
# Run me from the Workspace root like this:
#   ./bazel-out/darwin-fastbuild/bin/src/python/testapp/testapp 5000 src/resources/testapp/ssl/server.pem 
#

certificate_file = None
port_number = None

def getStatic(filepath):
    root = [
        x for x in [
            './static/',
        ]
        if os.path.exists(os.path.join(str(x), str(filepath)))
    ]
    if not root:
        abort(404, "No such file.")
    return static_file(filepath, root=root[0])

def getRoot():
    msg = say_hello.say_hello()
    r = a_pb2.A()
    r.ParseFromString(msg)
    return r.data

def startWebServer(app):
    srv = SSLWSGIRefServer.SSLWSGIRefServer(host="0.0.0.0", port=port_number, certificate_file=certificate_file)
    run(server=srv, app=app)

def main():

    global port_number
    global certificate_file

    port_number = sys.argv[1]
    certificate_file = sys.argv[2]

    msg = say_hello.say_hello()
    result = a_pb2.A()
    result.ParseFromString(msg)
    print(result.data)

    app = Bottle()

    app.route('/', method='GET', callback=functools.partial(getRoot))
    app.route('/static/<filepath:path>', method='GET', callback=functools.partial(getStatic))

    startWebServer(app)

if __name__ == "__main__":
    main()
