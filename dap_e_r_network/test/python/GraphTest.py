import unittest
import sys

from dap_e_r_network.src.python import Graph

class GraphTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        self.g = Graph.Graph()

    def tearDown(self):
        """Call after every test case."""
        self.g = None

    def testSingleLink(self):
        self.g.addLink("A", "B")

        r = self.g.explore("A")
        assert len(r) == 1
        assert sorted(r) == [ "B" ]

    def testDoubleLinks(self):
        self.g.addLink("A", "B", label="bus")
        self.g.addLink("A", "B", label="train")

        r = self.g.explore("A")
        assert len(r) == 1
        assert sorted(r) == [ "B" ]

    def testDiamond(self):
        self.g.addLink("A", "B", label="bus")
        self.g.addLink("A", "C", label="bus")
        self.g.addLink("B", "D", label="bus")
        self.g.addLink("C", "D", label="bus")

        r = self.g.explore("A")
        assert len(r) == 3
        assert sorted(r) == [ "B", "C", "D" ]

    def testUnconnecteds(self):
        self.g.addLink("A", "B", label="bus")
        self.g.addLink("A", "C", label="bus")

        self.g.addLink("D", "E", label="bus")

        r = self.g.explore("A")
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]

        r = self.g.explore("D")
        assert len(r) == 1
        assert sorted(r) == [ "E" ]

    def testDirections(self):
        self.g.addLink("A", "B", label="bus")
        self.g.addLink("B", "C", label="bus")

        r = self.g.explore("A")
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]

        r = self.g.explore("B")
        assert len(r) == 1
        assert sorted(r) == [  "C" ]

        r = self.g.explore("C")
        assert len(r) == 0
        assert sorted(r) == [ ]

    def testBidirections(self):
        self.g.addLink("A", "B", label="bus", bidirectional=True)
        self.g.addLink("B", "C", label="bus", bidirectional=True)

        r = self.g.explore("A")
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]

        r = self.g.explore("B")
        assert len(r) == 2
        assert sorted(r) == [ "A", "C" ]

    def testDeletions(self):
        self.g.addLink("A", "B", label="bus", bidirectional=True)
        self.g.addLink("B", "C", label="bus", bidirectional=True)

        r = self.g.explore("A")
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]

        self.g.removeLink("B", "C", bidirectional=True)

        r = self.g.explore("A")
        assert len(r) == 1
        assert sorted(r) == [ "B" ]

    def testOneWayDeletions(self):
        self.g.addLink("A", "B", label="bus", bidirectional=True)
        self.g.addLink("B", "C", label="bus", bidirectional=True)

        r = self.g.explore("A")
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]

        self.g.removeLink("B", "C")

        r = self.g.explore("A")
        assert len(r) == 1
        assert sorted(r) == [ "B" ]


        r = self.g.explore("C")
        assert len(r) == 2
        assert sorted(r) == [ "A", "B" ]

    def testLinkLengthLimit(self):
        self.g.addLink("A", "B", label="bus", weight=6)
        self.g.addLink("A", "C", label="bus", weight=6)
        self.g.addLink("B", "D", label="bus", weight=6)
        self.g.addLink("C", "D", label="bus", weight=6)

        r = self.g.explore("A", filter_distance_function=lambda move, total: total<10)
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]

    def testLinksPickCheapOnes(self):
        self.g.addLink("A", "B", label="bus", weight=6)
        self.g.addLink("A", "C", label="bus", weight=6)
        self.g.addLink("B", "D", label="bus", weight=3)
        self.g.addLink("C", "D", label="bus", weight=6)

        r = self.g.explore("A", filter_distance_function=lambda move, total: total<10)
        assert len(r) == 3
        assert sorted(r) == [ "B", "C", "D" ]

    def testLinksCostsAreCheapests(self):
        self.g.addLink("A", "B", label="bus", weight=6)
        self.g.addLink("A", "C", label="bus", weight=6)
        self.g.addLink("B", "D", label="bus", weight=3)
        self.g.addLink("C", "D", label="bus", weight=6)

        r = self.g.exploreCosts("A", filter_distance_function=lambda move, total: total<10)
        assert len(r) == 3
        assert r == {
            "B": 6,
            "C": 6,
            "D": 9,
        }

    def testLinksCostsAreCheapestFromSeveralTypes(self):
        self.g.addLink("A", "B", label="bus", weight=6)
        self.g.addLink("A", "C", label="bus", weight=6)
        self.g.addLink("A", "C", label="train", weight=6)
        self.g.addLink("B", "D", label="bus", weight=3)
        self.g.addLink("B", "D", label="train", weight=2)
        self.g.addLink("C", "D", label="bus", weight=6)

        r = self.g.exploreCosts("A", filter_distance_function=lambda move, total: total<10)
        assert len(r) == 3
        assert r == {
            "B": 6,
            "C": 6,
            "D": 8,
        }

    def testLinksCostsAreCheapestFromSeveralAllowedTypes(self):
        self.g.addLink("A", "B", label="bus", weight=6)
        self.g.addLink("A", "C", label="bus", weight=8)
        self.g.addLink("A", "C", label="train", weight=6)
        self.g.addLink("B", "D", label="bus", weight=3)
        self.g.addLink("B", "D", label="teleportation", weight=2)
        self.g.addLink("C", "D", label="bus", weight=6)

        r = self.g.exploreCosts("A", filter_distance_function=lambda move, total: total<10,
                                    filter_move_function=lambda x: x in ["bus", "train"])
        assert len(r) == 3
        assert r == {
            "B": 6,
            "C": 6,
            "D": 9,
        }

    def testLinksFilteringKinds(self):
        self.g.addLink("A", "B", label="bus", weight=6)
        self.g.addLink("A", "C", label="train", weight=6)
        self.g.addLink("B", "D", label="bus", weight=3)
        self.g.addLink("C", "D", label="train", weight=6)

        r = self.g.explore("A", filter_move_function=lambda x: x == "bus")
        assert len(r) == 2
        assert sorted(r) == [ "B", "D" ]

    def testLoops(self):
        self.g.addLink("A", "B")
        self.g.addLink("B", "C", bidirectional=True)

        r = self.g.explore("A")
        assert len(r) == 2
        assert sorted(r) == [ "B", "C" ]
