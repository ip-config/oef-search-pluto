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

    # Bearing of POS2 from POS1 along a great circle.
    def InitialBearing(self, pos1, pos2):
        φ1,λ1 = pos1
        φ2,λ2 = pos2
        y = math.sin(λ2-λ1) * math.cos(φ2)
        x = math.cos(φ1)*math.sin(φ2) - math.sin(φ1)*math.cos(φ2)*math.cos(λ2-λ1)
        brng = math.degrees(math.atan2(y, x))
        return (brng + 360) % 360

    def search(self, location, radius_in_m, bearing=None, bearing_width=None):
        results = self.searchWithData(location, radius_in_m, bearing=bearing, bearing_width=bearing_width)
        for r in results:
            yield r[0]

    def searchWithData(self, location, radius_in_m, bearing=None, bearing_width=None):
        for entity, loc in self.store.items():
            d = self.EquirectangularDistance(location, loc)
            br = self.InitialBearing(location, loc)
            r = (entity, int(d), int(br))
            if d > radius_in_m:
                continue
            yield r
