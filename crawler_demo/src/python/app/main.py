#!/usr/bin/env python3

import argparse
import functools
import math
import os
import numpy as np
from PIL import Image, ImageOps
from england_grid.src.python.lib import EnglandGrid
from crawler_demo.src.python.lib.SearchNetwork import SearchNetwork, ConnectionFactory
from fake_oef.src.python.lib.FakeDirector import Observer

from england_grid.src.python.lib import World
from fetch_teams.bottle import bottle


class ActivityObserver(Observer):
    def on_change(self, node_id, value=None):
        pass


class App(object):
    def __init__(self):
        self.world = World.World()
        self.grid = EnglandGrid.EnglandGrid()

    def getRoot(self):
        return bottle.redirect("/svg")

    def getPop(self):
        return bottle.static_file("england_grid/resources/images/pop.png", root=os.getcwd())

    def getSVG(self):
        bottle.response.content_type = "image/svg+xml;charset=utf-8"
        return self.world.getSVG()

    def run(self, args):
        self.grid = EnglandGrid.EnglandGrid()
        self.grid.load()

        connection_factory = ConnectionFactory()
        search_network = SearchNetwork(connection_factory, self.grid.entities)
        search_network.build_from_entities(self.grid.entities)

        activity_observer = ActivityObserver()

        search_network.register_activity_observer(activity_observer)

        self.server = bottle.Bottle()
        self.server.route('/', method='GET', callback=functools.partial(self.getRoot))
        self.server.route('/svg', method='GET', callback=functools.partial(self.getSVG))
        self.server.route('/pop', method='GET', callback=functools.partial(self.getPop))
        self.server.route('/genpop', method='GET', callback=functools.partial(self.genPop))
        self.server.run(host="0.0.0.0", port=args.http_port)





def main():
    app = App()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--http_port",        required=True, type=int, help="which port to run the HTTP interface on.")

    args = parser.parse_args()
    app.run(args)

if __name__ == '__main__':
    main()

