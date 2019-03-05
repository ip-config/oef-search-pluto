import time

from crawler_demo.src.python.lib import CrawlerAgentBehaviour
from behaviour_tree.src.python.lib import BehaveTreeExecution

def main():
    tree = CrawlerAgentBehaviour.CrawlerAgentBehaviour()
    agent = BehaveTreeExecution.BehaveTreeExecution(tree)

    for i in range(0, 1000):
        agent.tick()
        print("At: {},{}    moving at {},{} towards: {},{}    target {},{}".format(
            agent.get('x'),
            agent.get('y'),
            agent.get('delta-x'),
            agent.get('delta-y'),
            agent.get('moveto-x'),
            agent.get('moveto-y'),
            agent.get('target-x'),
            agent.get('target-y'),
        ))
        #time.sleep(0.20)


if __name__ == '__main__':
    main()
