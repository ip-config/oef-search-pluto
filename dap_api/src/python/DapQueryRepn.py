from abc import ABC
from abc import abstractmethod

from fetch_teams.oef_core_protocol import query_pb2

class DapQueryRepn(object):

    class Branch(object):
        def __init__(self,
                combiner=None,
                **kwargs):
            self.leaves = []
            self.subnodes = []
            self.type = None
            self.combiner = combiner
            self.common_target_table_name = None
            self.common_dap_name = None

        def printable(self):
            return "{} over {}, {}".format(
                self.combiner,
                self.common_target_table_name,
                self.common_dap_name
                )

        def print(self, depth=0):
            for n in self.subnodes:
                n.print(depth+1)
            for leaf in self.leaves:
                print((depth+1)*"  ", leaf.printable())

    class Leaf(object):
        def __init__(self,
                operator=None,
                query_field_type=None,
                query_field_value=None,
                target_field_type=None,
                target_field_name=None,
                target_table_name=None,
                dap_name=None,
                **kwargs
                     ):
            self.operator          = operator

            self.query_field_value = query_field_value
            self.query_field_type  = query_field_type

            self.target_field_name = target_field_name
            self.target_field_type = target_field_type
            self.target_table_name = target_table_name

            self.dap_name          = dap_name

        def printable(self):
            return "{}.{}.{} ({}) {} {} ({})".format(
                self.dap_name,
                self.target_table_name,
                self.target_field_name,
                self.target_field_type,
                self.operator,
                self.query_field_value,
                self.query_field_type
                )

    class Visitor(ABC):
        def init(self):
            pass

        @abstractmethod
        def visitNode(self, node, depth):
            pass

        @abstractmethod
        def visitLeaf(self, leaf, depth):
            pass

    def print(self):
        self.root.print()

    def __init__(self):
        self.root = DapQueryRepn.Branch(combiner="all")

    def visit(self, visitor, node=None, depth=0):
        if not node:
            node = self.root
        if not node:
            return

        #print("DEPTH ", depth, " SUBS=", node.subnodes, " LVS=", node.leaves)
        for subnode in node.subnodes:
            #print("VISIT SUB ", depth+1)
            self.visit(visitor, subnode, depth+1)
        for leaf in node.leaves:
            #print("VISIT LEAF ", depth+1)
            visitor.visitLeaf(leaf, depth+1)
        visitor.visitNode(node, depth)

    def _VALUE_toTypeVal(self, value_pb):
        if value_pb.HasField("s"):
            return ("string", value_pb.s)
        if value_pb.HasField("d"):
            return ("double", value_pb.d)
        if value_pb.HasField("b"):
            return ("bool", value_pb.b)
        if value_pb.HasField("i"):
            return ("int64", value_pb.i)
        if value_pb.HasField("l"):
            return ("location", (value_pb.l.lat, value_pb.l.lon))
        return (None, None)

    def _SET_VALUES_toTypeVal(self, values_pb):
        if value_pb.HasField("s"):
            return ("string_list", values_pb.s)
        if value_pb.HasField("d"):
            return ("double_list", values_pb.d)
        if value_pb.HasField("b"):
            return ("bool_list", values_pb.b)
        if value_pb.HasField("i"):
            return ("int64_list", values_pb.i)
        if value_pb.HasField("l"):
            return ("location_list", [
                (foo.lat, foo.lon) for foo in values_pb.l])
        return (None, None)

    def _RANGE_VALUES_toTypeVal(self, values_pb):
        if value_pb.HasField("s"):
            return ("string_range", (values_pb.s.first, values_pb.s.second))
        if value_pb.HasField("d"):
            return ("double_range", (values_pb.d.first, values_pb.d.second))
        if value_pb.HasField("i"):
            return ("int64_range", (values_pb.i.first, values_pb.i.second))
        if value_pb.HasField("l"):
            return ("location_range", ((values_pb.l.first.lat, values_pb.l.first.lon), (values_pb.l.second.lat, values_pb.l.second.lon)))
        return (None, None)

    def _CONSTRAINT_SET_toRepn(self, set_pb, attr_name):
        comparator = {
            0: "IN",
            1: "NOTIN",
        }[set_pb.op]
        query_field_type, query_field_value = self._SET_VALUES_toTypeVal(set_pb.vals)
        return DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=query_field_value,
            query_field_type=query_field_type,
            target_field_name=attr_name
        )

    def _CONSTRAINT_EMBEDDING_toRepn(self, embedding_pb, attr_name):
        comparator = {
            0: "CLOSETO",
        }[embedding_pb.op]

        resultdata = list(embedding_pb.val.v)
        return DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=resultdata,
            query_field_type="embedding",
            target_field_name=attr_name,
        )

    def _CONSTRAINT_RELATION_toRepn(self, relation_pb, attr_name):
        comparator = {
            0: "==",
            1: "<",
            2: "<=",
            3: ">",
            4: ">=",
            5: "!=",
        }[relation_pb.op]
        query_field_type, query_field_value = self._VALUE_toTypeVal(relation_pb.val)
        return DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=query_field_value,
            query_field_type=query_field_type,
            target_field_name=attr_name,
        )

    def _CONSTRAINT_RANGE_toRepn(self, range_pb, attr_name):
        comparator = "IN"
        attr_type = field_types.get(attr_name, {}).get('type', None)
        query_field_type, query_field_value = self._RANGE_VALUES_toTypeVal(range_pb.vals)
        return DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=query_field_value,
            query_field_type=query_field_type,
            target_field_name=attr_name,
        )

    def _CONSTRAINT_DISTANCE_toRepn(self, distance_pb, attr_name):
        pass

    def _CONSTRAINT_toRepn(self, constraint_pb):
        attr_name = constraint_pb.attribute_name
        if constraint_pb.HasField("set_"):
            return self._CONSTRAINT_SET_toRepn(constraint_pb.set_, attr_name)

        if constraint_pb.HasField("range_"):
            return self._CONSTRAINT_RANGE_toRepn(constraint_pb.range_, attr_name)

        if constraint_pb.HasField("relation"):
            return self._CONSTRAINT_RELATION_toRepn(constraint_pb.relation, attr_name)

        if constraint_pb.HasField("distance"):
            return self._CONSTRAINT_DISTANCE_toRepn(constraint_pb.distance, attr_name)

        if constraint_pb.HasField("embedding"):
            return self._CONSTRAINT_EMBEDDING_toRepn(constraint_pb.embedding, attr_name)

        raise Exception("_CONSTRAINT_toRepn ==> None")

    def _CONSTRAINT_EXPR_toRepn(self, ce_pb):
        if ce_pb.HasField("constraint"):
            return self._CONSTRAINT_toRepn(ce_pb.constraint)

        if ce_pb.HasField("or_"):
            subs = ce_pb.or_.expr
            combiner = "any"
        elif ce_pb.HasField("and_"):
            subs = ce_pb.and_.expr
            combiner = "all"
        elif ce_pb.HasField("not_"):
            subs = ce_pb.not_.expr
            combiner = "none"
        else:
            raise Exception("_CONSTRAINT_EXPR_toRepn ==> None")

        r = DapQueryRepn.Branch(combiner=combiner)
        for x in subs:
            newnode = self._CONSTRAINT_EXPR_toRepn(x)
            if isinstance(newnode, DapQueryRepn.Branch):
                r.subnodes.append(newnode)
            else:
                print("NEW:", type(newnode))
                r.leaves.append(newnode)

        print("NEW:", type(r))
        return r

    def fromQueryProto(self, pb):
        print("Hmm")
        try:
            ce_pb = pb.constraints
        except AttributeError:
            ce_pb = pb
        try:
            self.data_model = pb.model
        except AttributeError:
            pass
        try:
            self.description = self.description
        except AttributeError:
            pass

        self.root.subnodes = [ self._CONSTRAINT_EXPR_toRepn(ce_pb) ]
