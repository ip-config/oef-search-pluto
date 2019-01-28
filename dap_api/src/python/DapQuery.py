
from fetch_teams.oef_core_protocol import query_pb2

class DapQuery:
    def __init__(self):
        self.comp = None

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
            return ("location", value_pb.l)
        return (None, None)

    def fromQueryProto(self, query_pb, constraint_factory, field_types):
        if query_pb.HasField("constraint"):
            constraint = query_pb.constraint
            if constraint.HasField("relation"):
                relation = constraint.relation
                comparator = {
                    0: "==",
                    1: "<",
                    2: "<=",
                    3: ">",
                    4: ">=",
                    5: "!=",
                }[relation.op]
            field_name = "wibble"
            field_type = field_types.get(field_name, {}).get('type', None)
            constant_type, constant_value = self._VALUE_toTypeVal(relation.val)
            self.comp = lambda row: constraint_factory.process(field_type, row.get(field_name, None), comparator, constant_type, constant_value)

    def testRow(self, row):
        if self.comp:
            return self.comp(row)
        return True
