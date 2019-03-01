import threading
import functools
import time

from pluto_app.src.python.app import SearchNetwork
from fake_oef.src.python.lib import ConnectionFactory
from fetch_teams.bottle import bottle
from utils.src.python import ThreadedWebserver
from fake_oef.src.python.lib import FakeOef
from fake_oef.src.python.lib import FakeBase

class EnglandMapWebserver(object):
    def __init__(self, args):
        self.search_network = SearchNetwork.SearchNetwork()
        self.connection_factory = ConnectionFactory.ConnectionFactory()

        self.app = bottle.Bottle()

        self.server = ThreadedWebserver.ThreadedWebserver(7500, self.app)
        self.server.run()

        for i in [ 0, 1, 2, 3 ]:
            self.search_network.add_stack(
                "oef-{}".format(i),
                "search-{}".format(i),
                communication_handler=None,
                connection_factory=self.connection_factory,
            )

    def run(self, *args, **kwargs):
        while True:
            print(
                FakeBase.FakeBase.visit(
                    functools.partial(self.call_all, 'identify'),
                    *args,
                    **kwargs
                )
            )
            time.sleep(2)

    def call_all(self, method, fake, *args, **kwargs):
        if hasattr(fake, method):
            return getattr(fake, method)(*args, **kwargs)
        return None
