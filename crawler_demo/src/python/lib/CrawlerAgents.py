import random
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

from crawler_demo.src.python.lib import CrawlerAgentBehaviour
from behaviour_tree.src.python.lib import BehaveTreeExecution
from svg_output.src.python.lib import SvgStyle
from svg_output.src.python.lib import SvgGraph
from svg_output.src.python.lib import SvgElements
from behaviour_tree.src.python.lib import BehaveTreeExecution
from crawler_demo.src.python.lib.SearchNetwork import SearchNetwork, ConnectionFactory
from utils.src.python.Logging import has_logger

class CrawlerAgents(object):

    @has_logger
    def __init__(self, connection_factory, grid):
        self.tree = CrawlerAgentBehaviour.CrawlerAgentBehaviour()
        self.grid = grid

        self.threadpool = ThreadPoolExecutor(max_workers=1)

        randomisers = [
            self.createRandomiser(x)
            for x
            in range(0,30)
        ]

        self.agents = [
            BehaveTreeExecution.BehaveTreeExecution(self.tree, randomiser=x)
            for x
            in randomisers
        ]
        locations = {}
        for key, entity in grid.entities.items():
            locations[entity.name] = entity.coords
        idx = 1
        for agent in self.agents:
            agent.set("connection_factory", connection_factory)
            agent.set("locations", locations)
            agent.set("index", idx)
            if idx % 2 == 0 and True:
                agent.set("movement_type", CrawlerAgentBehaviour.MovementType.FOLLOW_PATH)
            else:
                agent.set("movement_type", CrawlerAgentBehaviour.MovementType.CRAWL_ON_NODES)
            idx += 1

    def tick(self):
        def ticker(x):
            return x.tick()
        _ = self.threadpool.map(ticker, self.agents )

    def createRandomiser(self, sequence):
        r = random.Random()
        r.seed(sequence)
        return r

    def getSVG(self):
        locations = [
            (
                agent.get('movement_type'),
                agent.get('x'),
                agent.get('y'),
                agent.get('connection'),
                agent.get('target-x'),
                agent.get('target-y')
            )
            for agent
            in self.agents
        ]

        self.info(locations)

        colour1 = "white"
        colour2 = "black"

        crawler_styles = {
            CrawlerAgentBehaviour.MovementType.CRAWL_ON_NODES: {
                'dot': SvgStyle.SvgStyle({"fill-opacity": 1, " fill": colour1, " stroke-width": 0.1}),
                'line': SvgStyle.SvgStyle({"stroke": colour1, "stroke-width": 1}),
                'dashes': SvgStyle.SvgStyle({"stroke": colour1, "stroke-width": 1, "stroke-dasharray":"3 1" }),
            },
            CrawlerAgentBehaviour.MovementType.FOLLOW_PATH:{
                'dot': SvgStyle.SvgStyle({"fill-opacity": 1, " fill": colour2, " stroke-width": 0.1}),
                'line': SvgStyle.SvgStyle({"stroke": colour2, "stroke-width": 1}),
                'dashes': SvgStyle.SvgStyle({"stroke": colour2, "stroke-width": 1, "stroke-dasharray":"3 1" }),
            }
        }

        dots =  [
            SvgElements.SvgCircle(
                cx=x,
                cy=y,
                r=3,
                style = crawler_styles[movement_type]['dot']
            )
            for movement_type, x,y,_,_,_
            in locations
        ]

        g = SvgGraph.SvgGraph(*dots)

        linedata = [
            ( movement_type, x, y, self.grid.getPositionOf(conn) )
            for movement_type, x, y, conn, _, _
            in locations
        ]

        lines =  [
            SvgElements.SvgLine( x1=x, y1=y, x2=pos[0], y2=pos[1],  style = crawler_styles[movement_type]['line'])
            for movement_type,x,y,pos
            in linedata
            if pos != None
        ]

        g.add(*lines)

        targetlines =  [
            SvgElements.SvgLine( x1=x, y1=y, x2=tx, y2=ty,  style = crawler_styles[movement_type]['dashes'])
            for movement_type,x,y,_,tx,ty
            in locations
            if tx != None and ty != None
        ]
        g.add(*targetlines)

        return g
