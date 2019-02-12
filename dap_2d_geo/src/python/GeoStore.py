#really naive implementaiotn.

class GeoStore(object):
    def __init__(self, left=180, right=-180, top=75, bottom=-75):
        self.store = {}

    def place(self, entity, location):
        self.store[entity] = location

    def remove(self, entity):
        self.store.pop(entity, None)

    def search(self, location, radius):
        r2 = radius * radius
        for entity, loc in self.store.items():
            d = (
                (location[0]-loc[0]) * (location[0]-loc[0])
                +
                (location[1]-loc[1]) * (location[1]-loc[1])
                )
            if d < r2:
                yield entity

