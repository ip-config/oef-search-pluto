#really naive implementaiotn.

import math
from utils.src.python.Logging import has_logger

class GeoStore(object):
    @has_logger
    def __init__(self, left=180, right=-180, top=75, bottom=-75):
        self.store = {}

    def place(self, entity, location):
        self.store[entity] = location

    def getAllKeys(self):
        for k in self.store.keys():
            yield k

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
    def InitialBearing(pos1, pos2):
        φ1,λ1 = math.radians(pos1[0]), math.radians(pos1[1])
        φ2,λ2 = math.radians(pos2[0]), math.radians(pos2[1])
        y = math.sin(λ2-λ1) * math.cos(φ2)
        x = math.cos(φ1)*math.sin(φ2) - math.sin(φ1)*math.cos(φ2)*math.cos(λ2-λ1)
        ang = math.atan2(y, x)
        brng = math.degrees(ang)
        return int((brng + 360) % 360)

    def search(self, location, radius_in_m, bearing=None, bearing_width=None):
        results = self.searchWithData(location, radius_in_m, bearing=bearing, bearing_width=bearing_width)
        for r in results:
            yield r[0]

    def containsBearing(left, right, bearing):
        if right > left:
            if bearing > left and bearing < right:
                return True
        else:
            if bearing > left or bearing < right:
                return True
        return False

    def entityToData(self, location, entity):
        loc = self.store.get(entity, None)
        if loc == None:
            self.error("no data entity=", entity)
            return None
        d = self.EquirectangularDistance(location, loc)
        br = GeoStore.InitialBearing(location, loc)
        return (entity, int(d), int(br))

    def accept(self, entities, location, radius_in_m, bearing=None, bearing_width=None):
        left = None
        right = None

        if bearing != None and bearing_width != None:
            if bearing_width < 0:
                bearing_width = -1 * bearing_width
            left = (bearing - bearing_width + 360) % 360
            right = (bearing + bearing_width + 360) % 360

        self.error("entities=", entities)
        for entity in list(entities):
            self.error("entity=", entity)
            r = self.entityToData(location, entity)
            if r == None:
                continue
            self.error("data=", r)
            _, d, br = r
            if d > radius_in_m:
                continue
            if left != None:
                if not GeoStore.containsBearing(left, right, br):
                    continue
            yield r

    def searchWithData(self, location, radius_in_m, bearing=None, bearing_width=None):
        return self.accept(self.store.keys(), location, radius_in_m, bearing, bearing_width)
