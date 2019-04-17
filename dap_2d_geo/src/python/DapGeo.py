from typing import Callable
from typing import Sequence
import json

from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python import DapInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers
from dap_api.src.python import SubQueryInterface
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.python.DapInterface import decodeConstraintValue
from dap_api.src.python.DapInterface import encodeConstraintValue
from dap_2d_geo.src.python import GeoStore
from dap_api.src.protos import dap_interface_pb2
from utils.src.python.Logging import has_logger

class DapGeo(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    @has_logger
    def __init__(self, name, configuration):
        self.name = name
        self.geos = {}
        self.structure = configuration['structure']
        self.fields_by_table = {}
        self.log.update_local_name("DapGeo("+name+")")

        for table_name, fields in self.structure.items():
            self.geos[table_name] = GeoStore.GeoStore()
            for field_name, config in fields.items():

                if isinstance(config, dict):
                    t = config['type']
                    opt = set(config['options'])
                elif isinstance(config, str):
                    t = config
                    opt = set()
                else:
                    raise Exception("Unexpected specification for a field")
                self.fields_by_table.setdefault(table_name, {}).setdefault(field_name, {})['options'] = opt
                self.fields_by_table.setdefault(table_name, {}).setdefault(field_name, {})['type'] = t
        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()

    def configure(self, desc: dap_description_pb2.DapDescription) ->  dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness
        r.success = True

        for tableinfo in desc.table:
            self.geos[tableinfo.name] = GeoStore.GeoStore()
            for fieldinfo in tableinfo.field:
                self.fields_by_table.setdefault(table_name, {}).setdefault(fieldinfo.name, {})['options'] = fieldinfo.options
                self.fields_by_table.setdefault(table_name, {}).setdefault(fieldinfo.name, {})['type'] = fieldinfo.type

        return r

    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        for table_name in self.geos.keys():
            result_table = result.table.add()
            result_table.name = table_name

            result_field = result_table.field.add()
            result_field.name = table_name + ".location"
            result_field.type = "location"
            result_field.options.extend(self.fields_by_table.get(table_name, {}).get( table_name + ".location", {}).get('options', []))

            result_field = result_table.field.add()
            result_field.name = table_name + ".radius"
            result_field.type = "double"

            result_field = result_table.field.add()
            result_field.name = table_name + ".update"
            result_field.type = "location"
        return result

    def getGeoByTableName(self, table_name):
        return self.geos[table_name]

    class DapGeoQuery(SubQueryInterface.SubQueryInterface):
        NAMES = {
            "radius" : {
                "htoj": lambda x: x,
                "jtoh": lambda x: x,
            },
            "tablename" : {
                "htoj": lambda x: x,
                "jtoh": lambda x: x,
            },
            "locations" : {
                "htoj": lambda x: x,
                "jtoh": lambda x: x,
            },
        }

        def __init__(self, dap):
            self.radius = None
            self.locations = None
            self.tablename = None
            self.geo = None
            self.dap = dap

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

        def execute(self, entities):
            r = set()

            entities = set(entities)

            for location in self.locations:
                self.dap.info("TRYING:", entities)
                accepted = list(self.geo.accept(entities, location, self.radius))
                self.dap.info("OK=", accepted)
                for k in accepted:
                    r.add(k[0])
                    try:
                        entities.remove(k[0])
                    except KeyError as e:
                        pass
                    self.dap.warning("ACCEPT:", k[0])
            return r

        def toJSON(self):
            r = {}
            for k,funcs in DapGeo.DapGeoQuery.NAMES.items():
                v = getattr(self, k)
                encoded = funcs['htoj'](v)
                r[k] = encoded
            return json.dumps(r)

        def fromJSON(self, data):
            r = json.loads(data)
            for k,funcs in DapGeo.DapGeoQuery.NAMES.items():
                setattr(self, k, funcs['jtoh'](r.get(k, None)))
            return self

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        raise Exception("GeoQuery must be created from subtrees, not leaves")

    def prepare(self, proto: dap_interface_pb2.ConstructQueryObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        r = dap_interface_pb2.ConstructQueryMementoResponse()
        #print("NOD NAAME:", proto.node_name)

        # We'll let someone else handle any bigger branching logic.
        if len(proto.constraints) == 0 or len(proto.children) > 0:
            r.success = False
            return r
        # We'll let someone else handle anything which isn't an ALL
        if proto.operator != ProtoHelpers.COMBINER_ALL:
            #print("Not doing because not ALL")
            r.success = False
            return r

        geoQuery = DapGeo.DapGeoQuery(self)
        for constraint in proto.constraints:
            geoQuery.setTablename(constraint.target_table_name)

        processes = {
            (geoQuery.tablename + ".location", "location"):      lambda q,x: q.addLocation(x),
            (geoQuery.tablename + ".location", "location_list"): lambda q,x: q.addLocations(x),
            (geoQuery.tablename + ".radius", "double"):          lambda q,x: q.addRadius(x),
            (geoQuery.tablename + ".radius", "float"):           lambda q,x: q.addRadius(x),
            (geoQuery.tablename + ".radius", "int32"):             lambda q,x: q.addRadius(x),
            (geoQuery.tablename + ".radius", "int64"):             lambda q,x: q.addRadius(x),
        }

        for constraint in proto.constraints:
            func = processes.get((constraint.target_field_name, constraint.query_field_type), None)
            if func == None:
                self.warning("Query cannot be made from ", constraint.target_field_name, " & ", constraint.query_field_type)
                r.success = False
                return r
            else:
                func(geoQuery, decodeConstraintValue(constraint.query_field_value))

        geoQuery.setGeo(self.getGeoByTableName(geoQuery.tablename))

        if geoQuery.sanity():
            r.success = True
            r.memento = geoQuery.toJSON().encode('utf8')
        else:
            r.success = False

        return r

    def makeIdentifier(core,ag):
        r = dap_interface_pb2.Identifier()
        r.core = core
        r.agent = ag
        return r

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        geoQuery = DapGeo.DapGeoQuery(self)
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        j = query_memento.memento.decode("utf-8")
        geoQuery.fromJSON(j)

        geoQuery.setGeo(self.getGeoByTableName(geoQuery.tablename))

        coreagent_to_identifier = {}

        if input_idents.HasField('originator') and input_idents.originator:
            self.warning("geoQuery.tablename=", geoQuery.tablename)
            idents = list(self.geos[geoQuery.tablename].getAllKeys())
            self.warning("idents=", idents)
            coreagent_to_identifier = {}
        else:
            coreagent_to_identifier.update({
                (identifier.core, identifier.agent): identifier
                for identifier
                in input_idents.identifiers
            })
            idents = coreagent_to_identifier.keys()


        self.warning("idents=", idents)
        reply = dap_interface_pb2.IdentifierSequence()
        reply.originator = False

        for r in geoQuery.execute(set(idents)):
            c = reply.identifiers.add()
            if r in coreagent_to_identifier:
                c.CopyFrom(coreagent_to_identifier[r])
            else:
                c.core = r[0]
                c.agent = r[1]
        return reply

    def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
        raise Exception("GeoQuery must be created from subtrees, not leaves")

    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    def update(self, tfv: dap_update_pb2.DapUpdate.TableFieldValue)  -> dap_interface_pb2.Successfulness:

        self.warning(tfv)

        typecode, val = ProtoHelpers.decodeAttributeValueToTypeValue(tfv.value)
        r = dap_interface_pb2.Successfulness()
        r.success = True

        if typecode != 'location':
            r.success = False
            r.narrative = "DapGeo won't do " + typecode + " updates."
            return r

        entity = (tfv.key.core, tfv.key.agent)
        locn = (val.lat, val.lon)

        self.warning("storing ", entity, locn)
        self.geos[tfv.tablename].place( entity, locn)
        return r

    def listCores(self, tablename, fieldname):
        r = []
        for k in self.geos[tablename].getAllKeys():
            if k[1] == b'':
                latlon = self.geos[tablename].get(k)
                result = dap_update_pb2.DapUpdate.TableFieldValue()
                ProtoHelpers.populateUpdateTFV(result, fieldname, latlon, typename='location')
                result.key.core = k[0]
                result.tablename = tablename

                r.append(result)
        return r
