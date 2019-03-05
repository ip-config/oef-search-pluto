from crawler_demo.src.python.lib import CrawlerAgentBehaviour
from behaviour_tree.src.python.lib import BehaveTreeExecution
from svg_output.src.python.lib import SvgStyle
from svg_output.src.python.lib import SvgGraph
from svg_output.src.python.lib import SvgElements
from behaviour_tree.src.python.lib import BehaveTreeExecution

class CrawlerAgents(object):
    def __init__(self, grid):
        self.tree = CrawlerAgentBehaviour.CrawlerAgentBehaviour()
        self.grid = grid
        self.agents = [
            BehaveTreeExecution.BehaveTreeExecution(self.tree),
            BehaveTreeExecution.BehaveTreeExecution(self.tree),
            BehaveTreeExecution.BehaveTreeExecution(self.tree),
        ]

    def tick(self):
        _ = [ x.tick() for x in self.agents ]

    def getSVG(self):
        locations = [
            (
                agent.get('x'),
                agent.get('y'),
                agent.get('connection'),
                agent.get('target-x'),
                agent.get('target-y')
            )
            for agent
            in self.agents
        ]

        crawler_dot_style = SvgStyle.SvgStyle({"fill-opacity": 1, " fill": "black", " stroke-width": 0.1})
        crawler_line_style = SvgStyle.SvgStyle({"stroke": "black", "stroke-width": 1})
        crawler_targetline_style = SvgStyle.SvgStyle({"stroke": "black", "stroke-width": 1, "stroke-dasharray":"3 1" })

        dots =  [
            SvgElements.SvgCircle(
                cx=x,
                cy=y,
                r=3,
                style = crawler_dot_style
            )
            for x,y,_,_,_
            in locations
        ]

        g = SvgGraph.SvgGraph(*dots)

        linedata = [
            ( x, y, self.grid.getPositionOf(conn) )
            for x, y, conn, _, _
            in locations
        ]

        lines =  [
            SvgElements.SvgLine( x1=x, y1=y, x2=pos[0], y2=pos[1],  style = crawler_line_style)
            for x,y,pos
            in linedata
            if pos != None
        ]

        g.add(*lines)

        targetlines =  [
            SvgElements.SvgLine( x1=x, y1=y, x2=tx, y2=ty,  style = crawler_targetline_style)
            for x,y,_,tx,ty
            in linedata
            if tx != None and ty != None
        ]

        return g
