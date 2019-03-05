import csv
import math

from optimframe.src.python.openpopgrid import EnglandPopDistro
from england_grid.src.python.lib import colours
from optimframe.src.python.lib import popgrab

from svg_output.src.python.lib import SvgElements
from svg_output.src.python.lib import SvgStyle
from svg_output.src.python.lib import SvgGraph

class EnglandGrid(object):

    class GridEntity(object):
        _regionnumber = 1

        def __init__(self, name, coords, kind=None, attributes={}):
            self.name = name
            self.coords = coords
            self.kind = kind
            self.attributes = attributes
            self.links = []
            self.region = EnglandGrid.GridEntity._regionnumber
            EnglandGrid.GridEntity._regionnumber +=1

    def __init__(self):
        self.entities = {}
        self.entity_locations = {}

        self.pop = EnglandPopDistro.EnglandPopDistro()
        self.pop.load("optimframe/src/data")

    def load(self):
        self.loadAirports()
        self.loadCities()
        self.connectCities()
        self.connectAirports()
        self.connectAirportsAndCities()

    def getPositionOf(self, name):
        if name not in self.entities:
            return None
        return self.entities[name].coords

    def getSVG(self):

        airport_dot_style   = SvgStyle.SvgStyle({"fill-opacity": 1, " fill": "yellow", " stroke-width": 0.1})
        city_dot_style      = SvgStyle.SvgStyle({"fill-opacity": 1, " fill": "red", " stroke-width": 0.1})
        airport_line_style  = SvgStyle.SvgStyle({"stroke": " yellow", " stroke-width": 1})
        city_line_style     = SvgStyle.SvgStyle({"stroke": " red", " stroke-width": 1})
        transfer_line_style = SvgStyle.SvgStyle({"stroke": " orange", " stroke-width": 1})

        r = SvgGraph.SvgGraph()

        r.add(*[
            SvgElements.SvgCircle(
                cx=entity.coords[0],
                cy=entity.coords[1],
                r=3,
                style = {
                    "AIRPORT": airport_dot_style,
                    "CITY": city_dot_style,
                }[entity.kind]
            )
            for entity in self.entities.values()
        ])

        for entity in self.entities.values():
            for link in entity.links:
                target = link[0]
                kind = link[1]
                r.add(SvgElements.SvgLine(
                    x1 =entity.coords[0],
                    y1 =entity.coords[1],
                    x2 =target.coords[0],
                    y2 =target.coords[1],
                    cx=entity.coords[0], cy=entity.coords[1], r=3, style = {
                        "GND": city_line_style,
                        "AIR": airport_line_style,
                        "TXF": transfer_line_style,
                    }[kind]
                ))
        return r

    def print(self):
        class PrintVisitor(object):
            def __init__(self, grid):
                self.row = ""
                self.grid = grid

            def visit(self, x,y,p,character):
                e = self.grid.entity_locations.get((x,y), None)
                kind = "PLAIN"
                if e:
                    kind = e[0].kind
                    self.row += (
                        colours.COLOUR_CONTROL_CODES[
                    {
                        'AIRPORT': 'on-red',
                        'CITY': 'on-blue',
                        'PLAIN': '',
                    }[kind]] +
                    character + colours.COLOUR_CONTROL_CODES['off']
                    )
                else:
                    self.row += character

            def rowcomplete(self):
                print(self.row)
                self.row = ""

        self.pop.visit(PrintVisitor(self))

    def addEntity(self, entity):
        self.entities[entity.name] = entity
        self.entity_locations.setdefault(entity.coords, []).append(entity)

    def loadCities(self, fn="toby_loader/data/csv/centres-ordered-by-population.csv"):
        cities = 0
        with open(fn, "r") as fh:
            reader = csv.reader(fh)
            for citynumber, row in enumerate(reader):
                city = row[0]
                coords = (int(row[2]), 699-int(row[1]))
                pop = row[3]
                self.addEntity(EnglandGrid.GridEntity(city, coords, "CITY", { "pop": int(pop) }))
                cities += 1
                if cities >= 50:
                    break

    def connectAirportsAndCities(self):
        temp = popgrab.PopGrab(700, 700)
        r = {}

        for airport in [ x for x in self.entities.values() if x.kind == 'AIRPORT' ]:
            temp.put(airport.region, airport.coords[0], airport.coords[1])
            r[airport.region] = airport
        temp.run()

        for city in [ x for x in self.entities.values() if x.kind == 'CITY' ]:
            region = temp.read_reg(city.coords[0], city.coords[1])
            if region >= 0:
                airport = r[region]
                diff = abs(city.coords[0]-airport.coords[0]) + abs(city.coords[1]-airport.coords[1])
                if diff < 30:
                    city.links.extend([ (airport, "TXF") ])

    def connectAirports(self):
        temp = popgrab.PopGrab(700, 700)
        r = {}

        for airport in [ x for x in self.entities.values() if x.kind == 'AIRPORT' ]:
            temp.put(airport.region, airport.coords[0], airport.coords[1])
            r[airport.region] = airport
        temp.run()
        for airport in r.values():
            targs = temp.get_neigh(airport.region)
            airport.links.extend( [ (r[x], 'AIR') for x in targs ] )

    def connectCities(self):
        temp = popgrab.PopGrab(700, 700)
        r = {}

        for city in [ x for x in self.entities.values() if x.kind == 'CITY' ]:
            temp.put(city.region, city.coords[0], city.coords[1])
            r[city.region] = city
        temp.run()

        for city in r.values():
            targs = temp.get_neigh(city.region)
            city.links.extend([ (r[x], "GND") for x in targs ])

    def loadAirports(self, fn="dap_2d_geo/test/resources/GlobalAirportDatabase.txt", limit=None):
        with open("dap_2d_geo/test/resources/GlobalAirportDatabase.txt", "r") as f:
            for i in f.readlines():
                i = i.strip()
                parts = i.split(":")

                if len(parts)<16:
                    continue

                airport = parts[1]
                country = parts[4]

                lat = float(parts[14])
                lon = float(parts[15])

                if airport == 'N/A':
                    continue

                if limit != None:
                    if airport not in limit:
                        continue

                if lat == 0.0 and lon == 0.0:
                    continue

                os_grid_y, os_grid_x = EnglandGrid._latlonToOSGrid(lat, lon)
                os_grid_y = 699 - os_grid_y

                if os_grid_x < 0 or os_grid_x >= 700:
                    continue
                if os_grid_y < 0 or os_grid_y >= 700:
                    continue

                if sum([self.pop.get(x, os_grid_y) for x in range(os_grid_x-10, os_grid_x+10)]) == 0.0:
                    continue

                self.addEntity(EnglandGrid.GridEntity(airport, (os_grid_x, os_grid_y), "AIRPORT"))

    def _latlonToOSGrid(lat, lon):
          φ = math.radians(lat)
          λ = math.radians(lon)

          a = 6377563.396
          b = 6356256.909              # Airy 1830 major & minor semi-axes
          F0 = 0.9996012717                             # NatGrid scale factor on central meridian
          φ0 = math.radians(49)
          λ0 = math.radians(-2)  # NatGrid true origin is 49°N,2°W
          N0 = -100000
          E0 = 400000                     # northing & easting of true origin, metres
          e2 = 1 - (b*b)/(a*a)                          # eccentricity squared
          n = (a-b)/(a+b)
          n2 = n*n
          n3 = n*n*n         # n, n², n³

          cosφ = math.cos(φ)
          sinφ = math.sin(φ)
          ν = a*F0/math.sqrt(1-e2*sinφ*sinφ)            # nu = transverse radius of curvature
          ρ = a*F0*(1-e2)/math.pow(1-e2*sinφ*sinφ, 1.5) # rho = meridional radius of curvature
          η2 = ν/ρ-1                                    # eta = ?

          Ma = (1 + n + (5/4)*n2 + (5/4)*n3) * (φ-φ0)
          Mb = (3*n + 3*n*n + (21/8)*n3) * math.sin(φ-φ0) * math.cos(φ+φ0)
          Mc = ((15/8)*n2 + (15/8)*n3) * math.sin(2*(φ-φ0)) * math.cos(2*(φ+φ0))
          Md = (35/24)*n3 * math.sin(3*(φ-φ0)) * math.cos(3*(φ+φ0))
          M = b * F0 * (Ma - Mb + Mc - Md)              # meridional arc

          cos3φ = cosφ*cosφ*cosφ
          cos5φ = cos3φ*cosφ*cosφ
          tan2φ = math.tan(φ)*math.tan(φ)
          tan4φ = tan2φ*tan2φ

          I = M + N0
          II = (ν/2)*sinφ*cosφ
          III = (ν/24)*sinφ*cos3φ*(5-tan2φ+9*η2)
          IIIA = (ν/720)*sinφ*cos5φ*(61-58*tan2φ+tan4φ)
          IV = ν*cosφ
          V = (ν/6)*cos3φ*(ν/ρ-tan2φ)
          VI = (ν/120) * cos5φ * (5 - 18*tan2φ + tan4φ + 14*η2 - 58*tan2φ*η2)

          Δλ = λ-λ0
          Δλ2 = Δλ*Δλ
          Δλ3 = Δλ2*Δλ
          Δλ4 = Δλ3*Δλ
          Δλ5 = Δλ4*Δλ
          Δλ6 = Δλ5*Δλ

          N = I + II*Δλ2 + III*Δλ4 + IIIA*Δλ6
          E = E0 + IV*Δλ + V*Δλ3 + VI*Δλ5

          return (int(N/1000), int(E/1000))
