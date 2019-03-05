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
        return bottle.redirect("/svg")

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
                    r = 0.6
                    g = 0.8
                    b = 1.0
                else:
                    r = 0.75 - 0.75 * math.sqrt(math.sqrt(n))
                    g = r*1.1
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
        return """
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 700 700">
<g><image href="pop" x="0" y="0" height="700" width="700"/></g>
{}
</svg>
""".format(self.grid.getSVG().render())

    def run(self, args):
        self.grid = EnglandGrid.EnglandGrid()
        self.grid.load()

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

