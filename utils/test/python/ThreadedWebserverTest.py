import functools
import json
import random
import sys
import os
import unittest
import time
import requests

from utils.src.python import ThreadedWebserver
from fetch_teams.bottle import bottle
from fetch_teams.bottle import SSLWSGIRefServer

class ThreadedWebserverTest(unittest.TestCase):
    def __setUp__(self):
        pass


    def getRoot(self):
        return "Hello"

    def testKill(self):
        app = bottle.Bottle()
        app.route('/', method='GET', callback=functools.partial(self.getRoot))

        foo = ThreadedWebserver.ThreadedWebserver(7500, app)
        foo.run()

        time.sleep(1)

        r = requests.get('http://127.0.0.1:7500/')

        foo.stop()

        assert r.text == "Hello"
