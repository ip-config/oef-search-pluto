from typing import Callable
from typing import Sequence

from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python import DapInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers
from dap_api.src.python import SubQueryInterface
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_2d_geo.src.python import GeoStore

class DapGeo(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, configuration):
        self.name = name
        self.geos = {}
        self.structure_pb = configuration['structure']

        for table_name, fields in self.structure_pb.items():
            self.geos[table_name] = GeoStore.GeoStore()

        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()

    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        for table_name in self.geos.keys():
            result_table = result.table.add()
            result_table.name = table_name

            result_field = result_table.field.add()
            result_field.name = table_name + ".location"
            result_field.type = "location"

            result_field = result_table.field.add()
            result_field.name = table_name + ".radius"
            result_field.type = "double"

        return result

    def getGeoByTableName(self, table_name):
        return self.geos[table_name]

    class DapGeoQuery(SubQueryInterface.SubQueryInterface):
        def __init__(self):
            self.radius = None
            self.locations = None
            self.tablename = None
            self.geo = None

        def setGeo(self, geo):
            self.geo = geo

        def setTablename(self, tablename):
            if self.tablename != None and self.tablename != tablename:
                raise Exception("GeoQuery only supports one tablename")
            self.tablename = tablename

        def addRadius(self, radius):
            if self.radius != None:
                raise Exception("GeoQuery only supports one weight limit")
            self.radius = radius

        def addLocation(self, loc):
            if self.locations == None:
                self.locations = []
            self.locations.append(loc)

        def addLocations(self, locs):
            if self.locations == None:
                self.locations = []
            self.origins.extend(locs)

        def printable(self):
            return "{} < {}".format(
                self.locations,
                self.radius
            )

        def sanity(self):
            if self.locations == None:
                raise Exception("GeoQuery must have one or more origins")
            if self.radius == None:
                raise Exception("GeoQuery must have a search radius in METRES")
            return self

        def execute(self, agents: Sequence[str]=None):
            for location in self.locations:
                yield from self.geo.search( location, self.radius )

    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        # We'll let someone else handle any bigger branching logic.
        if len(dapQueryRepnBranch.leaves) == 0 or len(dapQueryRepnBranch.subnodes) > 0:
            return None

        # We'll let someone else handle anything which isn't an ALL
        if dapQueryRepnBranch.combiner != ProtoHelpers.COMBINER_ALL:
            return None

        geoQuery = DapGeo.DapGeoQuery()
        for leaf in dapQueryRepnBranch.leaves:
            geoQuery.setTablename(leaf.target_table_name)

        processes = {
            (geoQuery.tablename + ".location", "location"):      lambda q,x: q.addLocation(x),
            (geoQuery.tablename + ".location", "location_list"): lambda q,x: q.addLocations(x),
            (geoQuery.tablename + ".radius", "double"):          lambda q,x: q.addRadius(x),
            (geoQuery.tablename + ".radius", "float"):           lambda q,x: q.addRadius(x),
            (geoQuery.tablename + ".radius", "i32"):             lambda q,x: q.addRadius(x),
            (geoQuery.tablename + ".radius", "i64"):             lambda q,x: q.addRadius(x),
        }

        for leaf in dapQueryRepnBranch.leaves:
            func = processes.get((leaf.target_field_name, leaf.query_field_type), None)
            if func == None:
                raise Exception("GeoQuery cannot be made from " + leaf.printable())
            else:
                func(geoQuery, leaf.query_field_value)

        geoQuery.setGeo(self.getGeoByTableName(geoQuery.tablename))

        return geoQuery.sanity()

    def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
        raise Exception("GeoQuery must be created from subtrees, not leaves")

    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    def update(self, update_data: dap_update_pb2.DapUpdate.TableFieldValue):
        for commit in [ False, True ]:
            upd = update_data
            if upd:
                raise Exception("Not implemented")