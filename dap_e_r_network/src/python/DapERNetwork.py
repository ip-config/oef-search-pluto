from typing import Callable
from typing import Sequence
import json

from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos import dap_update_pb2
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.python import DapInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers
from dap_api.src.python import SubQueryInterface
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.python.DapInterface import decodeConstraintValue
from dap_api.src.python.DapInterface import encodeConstraintValue
from dap_e_r_network.src.python import Graph
from utils.src.python.Logging import has_logger

class DapERNetwork(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    @has_logger
    def __init__(self, name, configuration):
        self.name = name
        self.graphs = {}
        self.structure_pb = configuration['structure']

        for table_name, fields in self.structure_pb.items():
            self.graphs[table_name] = Graph.Graph()

        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()


    def configure(self, desc: dap_description_pb2.DapDescription) ->  dap_interface_pb2.Successfulness:
        raise Exception("EarlyInMemoryDap does not configure via this interface yet.")


    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        for table_name in self.graphs.keys():
            result_table = result.table.add()
            result_table.name = table_name

            result_field = result_table.field.add()
            result_field.name = table_name + ".origin"
            result_field.type = "string_pair"

            result_field = result_table.field.add()
            result_field.name = table_name + ".label"
            result_field.type = "string"

            result_field = result_table.field.add()
            result_field.name = table_name + ".weight"
            result_field.type = "double"

        return result

    def getGraphByTableName(self, table_name):
        return self.graphs[table_name]

    class DapGraphQuery(SubQueryInterface.SubQueryInterface):
        NAMES = {
            "weight": {
                "htoj": lambda x: x,
                "jtoh": lambda x: x,
            },
            "labels": {
                "htoj": lambda x: x,
                "jtoh": lambda x: x,
            },
            "origins": {
                "htoj": lambda x: x,
                "jtoh": lambda x: [ tuple(y) for y in x ],
            },
            "tablename": {
                "htoj": lambda x: x,
                "jtoh": lambda x: x,
            },
        }
        def __init__(self):
            self.weight = None
            self.labels = None
            self.origins = None
            self.tablename = None
            self.graph = None

        def toJSON(self):
            r = {}
            for k,funcs in DapERNetwork.DapGraphQuery.NAMES.items():
                v = getattr(self, k)
                encoded = funcs['htoj'](v)
                r[k] = encoded
                #print("TO JSON k=", k, "   v=", v,   " enc=", encoded)
            return json.dumps(r)

        def fromJSON(self, data):
            r = json.loads(data)
            for k,funcs in DapERNetwork.DapGraphQuery.NAMES.items():
                setattr(self, k, funcs['jtoh'](r.get(k, None)))
            return self

        def setGraph(self, graph):
            self.graph = graph

        def setTablename(self, tablename):
            if self.tablename != None and self.tablename != tablename:
                raise Exception("GraphQuery only supports one tablename")
            self.tablename = tablename

        def addWeight(self, weight):
            if self.weight != None:
                raise Exception("GraphQuery only supports one weight limit")
            self.weight = weight

        def addLabel(self, label):
            if self.labels == None:
                self.labels = []
            self.labels.append(label)

        def addLabels(self, labels):
            if self.labels == None:
                self.labels = []
            self.labels.extend(labels)

        def addOrigin(self, origin):
            if self.origins == None:
                self.origins = []
            self.origins.append(origin)

        def addOrigins(self, origins):
            if self.origins == None:
                self.origins = []
            self.origins.extend(origins)

        def addOrigin(self, origin):
            if self.origins == None:
                self.origins = []
            self.origins.append(origin)

        def addOriginStr(self, s):
            s = s.split(',')[0:2]
            if len(s) < 2:
                s.prepend("localhost")
            self.addOrigin(tuple(s))

        def addOriginStrList(self, origins):
            for i in origins:
                self.addOriginStr(i)

        def printable(self):
            return "{} via {} < {}".format(
                self.origins,
                self.labels if self.labels != None else "*",
                self.weight if self.labels != None else "inf",
            )

        def sanity(self):
            if self.origins == None:
                raise Exception("GraphQuery must have one or more origins")
            return self

        def execute(self, agents: Sequence[str]=None):
            filter_move_function = lambda x:  x in self.labels if self.labels != None else lambda x: True
            filter_distance_function = lambda move, total:  total < self.weight if self.weight != None else lambda move, total: True

            for origin in self.origins:
                yield from self.graph.explore(
                    origin,
                    filter_move_function=filter_move_function,
                    filter_distance_function=filter_distance_function
                )

    def prepare(self, proto: dap_interface_pb2.ConstructQueryObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        r = dap_interface_pb2.ConstructQueryMementoResponse()

        if len(proto.constraints) == 0 or len(proto.children) > 0:
            self.info("No, I only want branches without branches.")
            r.success = False
            return r

        # We'll let someone else handle anything which isn't an ALL
        if proto.operator != ProtoHelpers.COMBINER_ALL:
            self.info("No, I only want branches doing AND.")
            r.success = False
            return r

        graphQuery = DapERNetwork.DapGraphQuery()
        for constraint in proto.constraints:
            graphQuery.setTablename(constraint.target_table_name)

        processes = {
            (graphQuery.tablename + ".origin", "string"):      lambda q,x: q.addOriginStr(x),
            (graphQuery.tablename + ".origin", "string_list"): lambda q,x: q.addOriginsStrList(x),
            (graphQuery.tablename + ".origin", "string_pair"): lambda q,x: q.addOrigin(x),
            (graphQuery.tablename + ".origin", "string_pair_list"): lambda q,x: q.addOrigins(x),
            (graphQuery.tablename + ".label",  "string"):      lambda q,x: q.addLabel(x),
            (graphQuery.tablename + ".label",  "string_list"): lambda q,x: q.addLabels(x),
            (graphQuery.tablename + ".weight", "int"):         lambda q,x: q.addWeight(x),
            (graphQuery.tablename + ".weight", "double"):      lambda q,x: q.addWeight(x),
            (graphQuery.tablename + ".weight", "int32"):       lambda q,x: q.addWeight(x),
            (graphQuery.tablename + ".weight", "int64"):       lambda q,x: q.addWeight(x),
        }

        for constraint in proto.constraints:
            func = processes.get((constraint.target_field_name, constraint.query_field_type), None)
            if func == None:
                self.log.error("Graph Query cannot be made")
                r.success = False
                return r
            else:
                func(graphQuery, decodeConstraintValue(constraint.query_field_value))

        graphQuery.setGraph(self.graphs[graphQuery.tablename])

        if graphQuery.sanity():
            r.success = True
            r.memento = graphQuery.toJSON().encode('utf8')
            self.info("Yeah, that'll be ok.")
        else:
            self.info("No, the resultant query was not sane.")
            r.success = False
        return r

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        graphQuery = DapERNetwork.DapGraphQuery()
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        j = query_memento.memento.decode("utf-8")
        graphQuery.fromJSON(j)
        graphQuery.setGraph(self.graphs[graphQuery.tablename])

        if input_idents.HasField('originator') and input_idents.originator:
            idents = None
        else:
            idents = [ DapQueryResult(x) for x in input_idents.identifiers ]

        reply = dap_interface_pb2.IdentifierSequence()
        reply.originator = False
        #BUG(KLL): missing score out of the copy
        for core in graphQuery.execute(idents):
            c = reply.identifiers.add()
            c.core = core[0].encode("utf-8")
            c.agent = core[1].encode("utf-8")
        return reply

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        raise Exception("DapERNetwork must create queries from subtrees, not leaves")

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
