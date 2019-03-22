import functools
import itertools

class Graph(object):
    def __init__(self):
        self.store = {}

    def addLink(
            self,
            source=None,
            target=None,
            weight=1,
            label="link",
            bidirectional=False
            ):
        for s,t in [ (source, target) ] + ( [ (target, source) ] if bidirectional else [] ):
            self.store.setdefault(s, {}).setdefault(t, {})[label] = weight

    def removeLink(
            self,
            source=None,
            target=None,
            label=None,
            bidirectional=False
            ):
        for s,t in [ (source, target) ] + ( [ (target, source) ] if bidirectional else [] ):
            if s in self.store:
                if t in self.store[s]:
                    if label == None:
                        del self.store[s][t]
                    else:
                        if label in store[s][t]:
                            del self.store[s][t][label]
                        if len(self.store[s][t]) == 0:
                            del self.store[s][t]
                    if len(self.store[s]) == 0:
                        del self.store[s]

    def explore(
            self,
            origin
            ):

        visited_nodes = set([ origin ])
        current_nodes = set([ origin ])

        print("ORIGIN=", origin)

        while len(current_nodes) > 0:
            print("EXPLORE CYCLE")
            next_nodes = set()

            list_of_list_of_moves = [ self.store[x].keys() for x in current_nodes if x in self.store ]
            iterlist_of_moves = itertools.chain.from_iterable(list_of_list_of_moves)
            next_moves = set(iterlist_of_moves)
            next_nodes = next_moves - visited_nodes
            visited_nodes |= next_nodes
            current_nodes = next_nodes

        return list(visited_nodes)

    def exploreCosts(
            self,
            origin,
            filter_move_function = lambda label: True,
            filter_distance_function = lambda move, total: True
            ):

        visited_nodes = { origin: 0 }
        current_nodes = set([ origin ])

        while len(current_nodes) > 0:
            next_nodes = set()

            list_of_moves = []

            for source in current_nodes:
                dist = visited_nodes[source]
                for target in self.store.get(source, {}).keys():
                    all_moves = self.store[source][target].keys()
                    allowed_moves = sorted([
                        (label, weight)
                        for label, weight
                        in self.store[source][target].items()
                        if filter_move_function(label)
                    ], key=lambda x: x[1])

                    if len(allowed_moves)>0:
                        m = allowed_moves[0]
                        d = m[1]

                        if target in visited_nodes:
                            if visited_nodes[target]<(d+dist):
                                continue

                        if not filter_distance_function (d, dist+d):
                            continue

                        visited_nodes[target] = d+dist
                        next_nodes.add(target)
            current_nodes = next_nodes
        del visited_nodes[origin]
        return visited_nodes

    def explore(
            self,
            origin,
            filter_move_function = lambda label: True,
            filter_distance_function = lambda move, total: True
            ):
        visited_nodes = self.exploreCosts(
            origin=origin,
            filter_move_function=filter_move_function,
            filter_distance_function=filter_distance_function
        )
        return list(visited_nodes.keys())
