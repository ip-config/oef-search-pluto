#really naive implementaiotn.
#really naive implementaiotn.

import math
from utils.src.python.Logging import has_logger

class GeoStore(object):
    @has_logger
    def __init__(self, left=180, right=-180, top=75, bottom=-75):
        self.store = {}
        self.distance_limit = 5000000

    def place(self, entity, location):
        self.log.info("PLACE: {} at {}".format(entity, location))
        self.store[entity] = location

    def get(self, entity):
        return self.store.get(entity, None)

    def getAllKeys(self):
        for k in self.store.keys():
            yield k

    def remove(self, entity):
        self.store.pop(entity, None)

    # Approximation to great circle distance; SHORT DISTANCES ONLY!
    def EquirectangularDistance(pos1, pos2):

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

    def OSGridDistance(pos1, pos2):
        # Grid coords are in km east and km north from an origin off
        # the coast of Cornwall. It's a nominally flat grid so..

        # remember the result should be in METRES

        dx = (pos1[0]-pos2[0])*1000
        dy = (pos1[1]-pos2[1])*1000
        d = math.sqrt(dx*dx+dy*dy)
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

    def entityToData(self, location, entity, distance_calculator):
        entity2 = entity
        loc = self.store.get(entity, None)
        if loc == None:
            self.warning("no data for entity=", entity)
            entity = (entity[0], b'',)
            loc = self.store.get(entity, None)
            if loc == None:
                self.error("no data for entity=", entity)
                return None
        d = distance_calculator(location, loc)
        br = GeoStore.InitialBearing(location, loc)
        return (entity2, int(d), int(br), loc)

    def accept(self,
                   entities,
                   location,
                   radius_in_m,
                   bearing=None,
                   bearing_width=None,
                   distance_calculator = EquirectangularDistance
                   ):
        left = None
        right = None

        if bearing != None and bearing_width != None:
            if bearing_width < 0:
                bearing_width = -1 * bearing_width
            left = (bearing - bearing_width + 360) % 360
            right = (bearing + bearing_width + 360) % 360

        self.info("entities=", entities)
        for entity in list(entities):
            self.info("entity=", entity)
            r = self.entityToData(location, entity, distance_calculator=distance_calculator)
            if r == None:
                continue
            self.info("data=", r)
            _, d, br, target_loc = r

            #if d > self.distance_limit:
            #    self.warning("EquirectangularDistance distance {} is greater then the limit {}! "
            #                 "Probably coordinate problem! ".format(d, self.distance_limit))
            #    dx = (location[0]-target_loc[0])*1000
            #    dy = (location[1]-target_loc[1])*1000
            #    d = math.sqrt(dx*dx+dy*dy)
            #    self.info("Recalculated distance: ", d)

            if d > radius_in_m:
                continue
            if left != None:
                if not GeoStore.containsBearing(left, right, br):
                    continue
            yield r

    def searchWithData(self, location, radius_in_m, bearing=None, bearing_width=None):
        return self.accept(self.store.keys(), location, radius_in_m, bearing, bearing_width)
