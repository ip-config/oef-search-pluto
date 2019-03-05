#!/usr/bin/env python3

import argparse
import functools
import math
import time
import os
import numpy as np
import requests
from PIL import Image, ImageOps

#from england_grid.src.python.lib import World
from fetch_teams.bottle import bottle
from england_grid.src.python.lib import EnglandGrid
from crawler_demo.src.python.lib import CrawlerAgents
from utils.src.python import ThreadedWebserver

import utils.src.python.resources as resources

class App(object):
    def __init__(self):
        #self.world = World.World()
        self.grid = EnglandGrid.EnglandGrid()
        self.agents = CrawlerAgents.CrawlerAgents()
        self.app = bottle.Bottle()

    def getRoot(self):
        return bottle.redirect("/static/html/crawl.html")

    def getPop(self):
        return bottle.static_file("england_grid/resources/images/pop.png", root=os.getcwd())

    def getStatic(self, filepath):
        try:
            return resources.textfile(os.path.join("crawler_demo/resources",filepath))
        except Exception as ex:
            print(ex)
            bottle.abort(404, "No such file.")

    def getSVG(self):
        bottle.response.content_type = "image/svg+xml;charset=utf-8"
        return """
<g><image href="pop" x="0" y="0" height="700" width="700"/></g>
{}
{}
""".format(
        self.grid.getSVG().render(),
        self.agents.getSVG().render()
        )

    def start(self, args):
        self.grid = EnglandGrid.EnglandGrid()
        self.grid.load()

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
    app = App()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--http_port",        required=True, type=int, help="which port to run the HTTP interface on.")

    args = parser.parse_args()
    app.start(args)
    app.run()

if __name__ == '__main__':
    main()

