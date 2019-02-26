#!/usr/bin/env python3

import argparse
import functools
import math
import os
import numpy as np
from PIL import Image, ImageOps

from england_grid.src.python.lib import EnglandGrid
from fetch_teams.bottle import bottle

class App(object):
    def __init__(self):
        self.grid = None

    def getRoot(self):
        return "Hello"

    def getPop(self):
        return bottle.static_file("england_grid/resources/images/pop.png", root=os.getcwd())


    def genPop(self):
        m = float(self.grid.pop.max())

        print(m)

        array = np.empty([700, 700, 3])

        class RenderVisitor(object):
            def __init__(self, array):
                self.array = array
            def visit(self, x, y, p, **kwargs):
                n = float(p)
                n /= m

                if p == 0.0:
                    r = 0
                    g = 0.4
                    b = 0.8
                else:
                    r = 0.75 - 0.75 * math.sqrt(math.sqrt(n))
                    g = r
                    b = r

                self.array[y,x,0] = r*255
                self.array[y,x,1] = g*255
                self.array[y,x,2] = b*255

        self.grid.pop.visit(RenderVisitor(array))
        img = Image.fromarray(array.astype('uint8'), 'RGB')
        img.save('pop.png')#
        return bottle.static_file("pop.png", root=os.getcwd())

    def getSVG(self):
        bottle.response.content_type = "image/svg+xml;charset=utf-8"
        r = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 700 700">
            <g style="fill-opacity:0.7; stroke:black; stroke-width:0.05;">
            <image href="pop" x="0" y="0" height="700" width="700"/>
        """

        for entity in self.grid.entities.values():

            if entity.kind == "AIRPORT":
                r += """
                <circle cx="{}" cy="{}" r="3" style="fill-opacity:1.0; fill:yellow; stroke-width:0.1" />
                """.format(
                    entity.coords[0],
                    entity.coords[1],
                )
            elif entity.kind == "CITY":
                r += """
                <circle cx="{}" cy="{}" r="3" style="fill-opacity:1; fill:red; stroke-width: 0.1" id="{}"/>
                """.format(
                    entity.coords[0],
                    entity.coords[1],
                    entity.name
                )

        for entity in self.grid.entities.values():
            for link in entity.links:
                target = link[0]
                kind = link[1]
                colour = {
                    'GND':'red',
                    'AIR':'yellow',
                }[kind]
                r += """
<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" id="{}-{}" style="stroke: {}; stroke-width: 0.5"/>
""".format(
                    entity.coords[0], entity.coords[1],
                    target.coords[0], target.coords[1],
                    'black',
                    entity.name, target.name,
                    colour
                )

        r += """
            </g>
        </svg>
        """

        print(r)

        return r



    def run(self, args):
        self.grid = EnglandGrid.EnglandGrid()
        self.grid.loadAirports()
        self.grid.loadCities()
        self.grid.connectCities()
        self.grid.connectAirports()
        self.grid.connectAirportsAndCities()

        self.getPop()

        self.server = bottle.Bottle()
        self.server.route('/', method='GET', callback=functools.partial(self.getRoot))
        self.server.route('/svg', method='GET', callback=functools.partial(self.getSVG))
        self.server.route('/pop', method='GET', callback=functools.partial(self.getPop))
#        self.server.route('/static/<filepath:path>', method='GET', callback=functools.partial(getStatic, self))
        self.server.run(host="0.0.0.0", port=args.http_port)





def main():
    app = App()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--http_port",        required=True, type=int, help="which port to run the HTTP interface on.")

    args = parser.parse_args()
    app.run(args)

if __name__ == '__main__':
    main()

