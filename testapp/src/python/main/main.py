#!/usr/bin/env python

import functools
import json
import os
import threading
import sys

from third_party.bottle import SSLWSGIRefServer
from third_party.bottle.bottle import abort
from third_party.bottle.bottle import Bottle
from third_party.bottle.bottle import error
from third_party.bottle.bottle import hook
from third_party.bottle.bottle import redirect
from third_party.bottle.bottle import request
from third_party.bottle.bottle import response
from third_party.bottle.bottle import route
from third_party.bottle.bottle import run
from third_party.bottle.bottle import static_file
from third_party.bottle.bottle import template

from google.protobuf import json_format

from testapp.src.protos import a_pb2
from testapp.src.python.mainfuncs import say_hello



# Build me like this:
#   bazel build testapp/src/python:testapp
#
# Run me from the Workspace root like this:
#   ./bazel-bin/testapp/src/python/testapp 5000 testapp/src/resources/ssl/server.pem 
#
# https://127.0.0.1:5000/
#
#   Accept the certificate.

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
    r = json.loads(json_format.MessageToJson(r))
    return r

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
