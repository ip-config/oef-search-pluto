#!/usr/bin/env python3

import argparse
import functools
import math
import time
import os
import numpy as np
import requests
from PIL import Image, ImageOps
from england_grid.src.python.lib import EnglandGrid
from crawler_demo.src.python.lib.SearchNetwork import SearchNetwork, ConnectionFactory
from fake_oef.src.python.lib.FakeDirector import Observer
from utils.src.python.Logging import configure as configure_logging
#from england_grid.src.python.lib import World
from fetch_teams.bottle import bottle
from england_grid.src.python.lib import EnglandGrid
from crawler_demo.src.python.lib import CrawlerAgents
from utils.src.python import ThreadedWebserver
from fake_oef.src.python.lib import FakeAgent
from api.src.proto import query_pb2, response_pb2


class ActivityObserver(Observer):
    def on_change(self, node_id, value=None):
        pass


def build_query(target=(200, 200)):
    q = query_pb2.Query()
    q.model.description = "weather data"
    q.ttl = 1
    q.directed_search.target.geo.lat = target[0]
    q.directed_search.target.geo.lon = target[1]
    q.directed_search.distance.geo = 1e9
    return q


def best_oef_core(nodes):
    distance = 1e16
    result = None
    for node in nodes:
        for res in node.result:
            if res.distance < distance:
                distance = res.distance
                result = res
    return result


import utils.src.python.resources as resources

class App(object):
    def __init__(self):
        #self.world = World.World()
        self.grid = EnglandGrid.EnglandGrid()
        self.grid.load()
        connection_factory = ConnectionFactory()
        search_network = SearchNetwork(connection_factory, self.grid.entities)
        search_network.build_from_entities(self.grid.entities)

        self.agents = CrawlerAgents.CrawlerAgents(connection_factory, self.grid)
        self.app = bottle.Bottle()

    def getRoot(self):
        return bottle.redirect("/static/html/crawl.html")

    def getPop(self):
        return bottle.static_file("england_grid/resources/images/pop.png", root=os.getcwd())

    def getStatic(self, filepath):
        try:
            return resources.textfile(os.path.join("crawler_demo/resources",filepath))
        except Exception as ex:
            bottle.abort(404, "No such file.")

    def getSVG(self):
        bottle.response.content_type = "image/svg+xml;charset=utf-8"
        return """<g><image href="pop" x="0" y="0" height="700" width="700" preserveAspectRatio="1"/></g>{}{}""".format(
        self.grid.getSVG().render(),
        self.agents.getSVG().render()
        )

    def start(self, args):
        #self.grid = EnglandGrid.EnglandGrid()
        #self.grid.load()

        #connection_factory = ConnectionFactory()
        #search_network = SearchNetwork(connection_factory, self.grid.entities)
        #search_network.build_from_entities(self.grid.entities)

        #activity_observer = ActivityObserver()

        #search_network.register_activity_observer(activity_observer)

        #target = "Leeds"
        #source = "Southampton"

        #agent = FakeAgent.FakeAgent(connection_factory=connection_factory, id="car")
        #agent.connect(target=source+"-core")
        #query = build_query((200, 200))
        #result = best_oef_core(agent.search(query))
        #loc = agent.get_from_core("location")
        #print("CURRENT AGENT LOC: ", loc.lon, loc.lon)
        #agent.swap_core(result)
        #loc = agent.get_from_core("location")
        #print("NEW AGENT LOC: ", loc.lon, loc.lon)

        self.app.route('/', method='GET', callback=functools.partial(self.getRoot))
        self.app.route('/static/<filepath:path>', method='GET', callback=functools.partial(self.getStatic))
        self.app.route('/svg', method='GET', callback=functools.partial(self.getSVG))
        self.app.route('/pop', method='GET', callback=functools.partial(self.getPop))

        self.server = ThreadedWebserver.ThreadedWebserver(args.http_port, self.app)

    def run(self):
        self.server.run()

        while True:
            self.agents.tick()
            time.sleep(0.1)


def main():
    configure_logging()
    app = App()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--http_port",        required=True, type=int, help="which port to run the HTTP interface on.")

    args = parser.parse_args()
    app.start(args)
    app.run()

if __name__ == '__main__':
    main()

