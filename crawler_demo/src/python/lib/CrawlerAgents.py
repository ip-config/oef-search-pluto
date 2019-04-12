import random
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

from crawler_demo.src.python.lib import CrawlerAgentBehaviour
from behaviour_tree.src.python.lib import BehaveTreeExecution
from svg_output.src.python.lib import SvgStyle
from svg_output.src.python.lib import SvgGraph
from svg_output.src.python.lib import SvgElements
from behaviour_tree.src.python.lib import BehaveTreeExecution
from utils.src.python.Logging import has_logger

DEFAULT_KINDS = [
    CrawlerAgentBehaviour.MovementType.FOLLOW_PATH,
    CrawlerAgentBehaviour.MovementType.CRAWL_ON_NODES,
]

class CrawlerAgents(object):

    @has_logger
    def __init__(self, oef_agent_factory, grid, kinds=DEFAULT_KINDS, agentcount=30):
        self.tree = CrawlerAgentBehaviour.CrawlerAgentBehaviour()
        self.grid = grid

        self.threadpool = ThreadPoolExecutor(max_workers=1)

        for k in kinds:
            if k not in DEFAULT_KINDS:
                print("Bad kind1:", k)
                print("Bad kind1:", DEFAULT_KINDS)
                print("Bad kind1:", type(k))
                print("Bad kind1:", [ type(kk) for kk in DEFAULT_KINDS])
                print("Bad kind1:", [ kk == k for kk in DEFAULT_KINDS])
                exit(77)
        randomisers = [
            self.createRandomiser(x)
            for x
            in range(0, agentcount)
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
            settings = oef_agent_factory.create("car-"+str(idx))

            for k,v in settings.items():
                agent.set(k, v)

            agent.set("locations", locations)
            agent.set("index", idx)
            agent.set("movement_type", kinds[ idx % len(kinds) ])
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

        kinds = set([
            agent.get('movement_type')
             for agent
            in self.agents
        ])
        for k in kinds:
            if k not in DEFAULT_KINDS:
                print("Bad kind:", k, DEFAULT_KINDS)
                exit(77)
            if k not in crawler_styles:
                print("Unstyled kind:", k, list(crawler_styles.keys()))
                exit(77)

        self.info(locations)


        dots =  []
        for movement_type, x,y,_,_,_ in locations:
            style = crawler_styles[movement_type]['dot']
            dots.append(SvgElements.SvgCircle(
                cx=x,
                cy=y,
                r=3,
                style=style
            ))

        g = SvgGraph.SvgGraph(*dots)

        #print([
        #    (conn, self.grid.getPositionOf(conn) or (100,100))
        #    for movement_type, x, y, conn, _, _
        #    in locations
        #])

        linedata = [
            ( movement_type, x, y, self.grid.getPositionOf(conn)  or (100,100))
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
