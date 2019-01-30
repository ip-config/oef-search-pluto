
from fetch_teams.oef_core_protocol import query_pb2


class DapQuery:
    def __init__(self):
        self.comp = None
        self.data_model = None

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

    def _CONSTRAINT_SET_toRowProcess(self, set_pb, attr_name):
        comparator = {
            0: "IN",
            1: "NOTIN",
        }[set_pb.op]
        attr_type = field_types.get(attr_name, {}).get('type', None)
        constant_type, constant_value = self._SET_VALUES_toTypeVal(set_pb.vals)
        return lambda row: constraint_factory.process(attr_type, row.get(attr_name, None), comparator, constant_type, constant_value)

    def _CONSTRAINT_EMBEDDING_toRowProcess(self, embedding_pb, attr_name, constraint_factory, field_types):
        comparator = {
            0: "CLOSETO",
        }[embedding_pb.op]
        attr_type = field_types.get(attr_name, {}).get('type', None)

        resultdata = list(embedding_pb.val.v)

        constant_type, constant_value = ("embedding", resultdata)
        return lambda row: constraint_factory.process(attr_type, row.get(attr_name, None), comparator, constant_type, constant_value)

    def _CONSTRAINT_RELATION_toRowProcess(self, relation_pb, attr_name, constraint_factory, field_types):
        comparator = {
            0: "==",
            1: "<",
            2: "<=",
            3: ">",
            4: ">=",
            5: "!=",
        }[relation_pb.op]
        attr_type = field_types.get(attr_name, {}).get('type', None)
        constant_type, constant_value = self._VALUE_toTypeVal(relation_pb.val)
        return lambda row: constraint_factory.process(attr_type, row.get(attr_name, None), comparator, constant_type, constant_value)

    def _CONSTRAINT_RANGE_toRowProcess(self, range_pb, attr_name):
        comparator = "IN"
        attr_type = field_types.get(attr_name, {}).get('type', None)
        constant_type, constant_value = self._RANGE_VALUES_toTypeVal(range_pb.vals)
        return lambda row: constraint_factory.process(attr_type, row.get(attr_name, None), comparator, constant_type, constant_value)

    def _CONSTRAINT_DISTANCE_toRowProcess(self, distance_pb, attr_name):
        pass

    def _CONSTRAINT_toRowProcess(self, constraint_pb, constraint_factory, field_types):
        attr_name = constraint_pb.attribute_name
        if constraint_pb.HasField("set_"):
            return self._CONSTRAINT_SET_toRowProcess(constraint_pb.set_, attr_name, constraint_factory, field_types)

        if constraint_pb.HasField("range_"):
            return self._CONSTRAINT_RANGE_toRowProcess(constraint_pb.range_, attr_name, constraint_factory, field_types)

        if constraint_pb.HasField("relation"):
            return self._CONSTRAINT_RELATION_toRowProcess(constraint_pb.relation, attr_name, constraint_factory, field_types)

        if constraint_pb.HasField("distance"):
            return self._CONSTRAINT_DISTANCE_toRowProcess(constraint_pb.distance, attr_name, constraint_factory, field_types)

        if constraint_pb.HasField("embedding"):
            return self._CONSTRAINT_EMBEDDING_toRowProcess(constraint_pb.embedding, attr_name, constraint_factory, field_types)

        raise Exception("_CONSTRAINT_toRowProcess ==> None")

    def _CONSTRAINT_EXPR_toRowProcess(self, ce_pb, constraint_factory, field_types):
        if ce_pb.HasField("constraint"):
            return self._CONSTRAINT_toRowProcess(ce_pb.constraint, constraint_factory, field_types)

        if ce_pb.HasField("or_"):
            subops = [
                self._CONSTRAINT_EXPR_toRowProcess(x, constraint_factory, field_types)
                for x in ce_pb.or_.expr
            ]
            return lambda row: any([ x(row) for x in subops if x ])

        if ce_pb.HasField("and_"):
            subops = [
                self._CONSTRAINT_EXPR_toRowProcess(x, constraint_factory, field_types)
                for x in ce_pb.and_.expr
            ]
            return lambda row: all([ x(row) for x in subops if x])

        if ce_pb.HasField("not_"):
            subops = [
                self._CONSTRAINT_EXPR_toRowProcess(x, constraint_factory, field_types)
                for x in ce_pb.not_.expr
            ]
            return lambda row: not(any([ x(row) for x in subops if x ]))

        raise Exception("_CONSTRAINT_toRowProcess ==> None")

    def fromQueryProto(self, pb, constraint_factory, field_types):
        if pb.HasField("constraints"):
            ce_pb = pb.constraints
            self.data_model = pb.model
        else:
            ce_pb = pb
        self.comp = self._CONSTRAINT_EXPR_toRowProcess(ce_pb, constraint_factory, field_types)

    def testRow(self, row):
        if self.comp:
            return self.comp(row)
        return True
