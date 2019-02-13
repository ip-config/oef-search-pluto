#really naive implementaiotn.

import math

class GeoStore(object):
    def __init__(self, left=180, right=-180, top=75, bottom=-75):
        self.store = {}

    def place(self, entity, location):
        self.store[entity] = location

    def remove(self, entity):
        self.store.pop(entity, None)

    # Approximation to great circle distance; SHORT DISTANCES ONLY!
    def EquirectangularDistance(self, pos1, pos2):

        radius = 6371000  # Earth's mean radius in m.

        phi1 = math.radians(pos1[0])
        lam1 = math.radians(pos1[1])

        phi2 = math.radians(pos2[0])
        lam2 = math.radians(pos2[1])

        # https://www.movable-type.co.uk/scripts/philong.html
        x = (lam2-lam1) * math.cos((phi1+phi2)/2);
        y = (phi2-phi1);
        d = math.sqrt((x*x + y*y)) * radius;
        return d

    def search(self, location, radius_in_m):
        for entity, loc in self.store.items():
            d = self.EquirectangularDistance(location, loc)
            if d < radius_in_m:
                yield entity

    def searchWithDistances(self, location, radius_in_m):
        for entity, loc in self.store.items():
            d = self.EquirectangularDistance(location, loc)
            r = (entity, d)
            if d < radius_in_m:
                yield r

