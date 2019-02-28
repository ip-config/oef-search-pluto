import unittest
import sys
import json
import random

from fake_oef.src.python.lib import ConnectionFactory
from fake_oef.src.python.lib import FakeOef
from fake_oef.src.python.lib import FakeAgent

def subset(kv, klist):
    return dict([ (k,v) for k,v in kv.items() if k in klist ])

class FakeOefTest(unittest.TestCase):
    AGENTS = [
        {'id': "agent_001", 'target': "oef_001"},
        {'id': "agent_002", 'target': "oef_001"},
        {'id': "agent_003", 'target': "oef_001"},
        {'id': "agent_004", 'target': "oef_002"},
    ]

    def setUp(self):
        """Call before every test case."""

        self.connection_factory = ConnectionFactory.ConnectionFactory()
        self.oef1 = FakeOef.FakeOef(id="oef_001", connection_factory=self.connection_factory)
        self.oef2 = FakeOef.FakeOef(id="oef_002", connection_factory=self.connection_factory)

    def tearDown(self):
        killables = [ self.oef1, self.oef2 ] + getattr(self, 'agents', [])
        random.shuffle(killables)
        for a in killables:
            a.kill()

    def testRegistration(self):

        self.agents = [
            FakeAgent.FakeAgent(connection_factory=self.connection_factory, id=x['id'])
            for x
            in FakeOefTest.AGENTS
        ]

        _ = [
            agent.connect(target=x['target'], subject=None)
            for agent, x
            in zip(self.agents, FakeOefTest.AGENTS)
        ]

        assert len(self.oef1.connections) == 3
        assert len(self.oef2.connections) == 1
