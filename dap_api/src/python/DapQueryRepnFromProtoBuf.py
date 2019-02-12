from abc import ABC
from abc import abstractmethod

from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers

class DapQueryRepnFromProtoBuf(object):
    def __init__(self):
        pass

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
        if values_pb.HasField("s"):
            return ("string_list", values_pb.s.vals)
        if values_pb.HasField("d"):
            return ("double_list", values_pb.d.vals)
        if values_pb.HasField("b"):
            return ("bool_list", values_pb.b.vals)
        if values_pb.HasField("i"):
            return ("int64_list", values_pb.i.vals)
        if values_pb.HasField("l"):
            return ("location_list", [
                (foo.lat, foo.lon) for foo in values_pb.l.vals])
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
            0: ProtoHelpers.OPERATOR_IN,
            1: ProtoHelpers.OPERATOR_NOT_IN,
        }[set_pb.op]
        query_field_type, query_field_value = self._SET_VALUES_toTypeVal(set_pb.vals)
        return DapQueryRepn.DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=query_field_value,
            query_field_type=query_field_type,
            target_field_name=attr_name
        )

    def _CONSTRAINT_EMBEDDING_toRepn(self, embedding_pb, attr_name):
        comparator = {
            0: ProtoHelpers.OPERATOR_CLOSE_TO,
        }[embedding_pb.op]

        resultdata = list(embedding_pb.val.v)
        return DapQueryRepn.DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=resultdata,
            query_field_type="embedding",
            target_field_name=attr_name,
        )

    def _CONSTRAINT_RELATION_toRepn(self, relation_pb, attr_name):
        comparator = {
            0: ProtoHelpers.OPERATOR_EQ,
            1: ProtoHelpers.OPERATOR_LT,
            2: ProtoHelpers.OPERATOR_LE,
            3: ProtoHelpers.OPERATOR_GT,
            4: ProtoHelpers.OPERATOR_GE,
            5: ProtoHelpers.OPERATOR_NE,
        }[relation_pb.op]
        query_field_type, query_field_value = self._VALUE_toTypeVal(relation_pb.val)
        return DapQueryRepn.DapQueryRepn.Leaf(
            operator=comparator,
            query_field_value=query_field_value,
            query_field_type=query_field_type,
            target_field_name=attr_name,
        )

    def _CONSTRAINT_RANGE_toRepn(self, range_pb, attr_name):
        comparator = "IN"
        attr_type = field_types.get(attr_name, {}).get('type', None)
        query_field_type, query_field_value = self._RANGE_VALUES_toTypeVal(range_pb.vals)
        return DapQueryRepn.DapQueryRepn.Leaf(
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
            combiner = ProtoHelpers.COMBINER_ANY
        elif ce_pb.HasField("and_"):
            subs = ce_pb.and_.expr
            combiner = ProtoHelpers.COMBINER_ALL
        elif ce_pb.HasField("not_"):
            subs = ce_pb.not_.expr
            combiner = ProtoHelpers.COMBINER_NONE
        else:
            raise Exception("_CONSTRAINT_EXPR_toRepn ==> None")

        r = DapQueryRepn.DapQueryRepn.Branch(combiner=combiner)
        for x in subs:
            newnode = self._CONSTRAINT_EXPR_toRepn(x)
            r.Add(newnode)
        return r

    def fromQueryConstraintsProto(self, pb):
        ce_pb = pb
        return self._CONSTRAINT_EXPR_toRepn(ce_pb)

    # this is used by the SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY hack
    def createEmbeddingMatchDataModel(self, embeddingInfo, data_model):
        #vector = embeddingInfo.createEmbedding(data_model)
        #resultdata = list(vector)

        return DapQueryRepn.DapQueryRepn.Leaf(
            operator=OPERATOR_CLOSE_TO,
            query_field_value=data_model,
            query_field_type="data_model",
            target_field_name=embeddingInfo.FieldName,
            target_table_name=embeddingInfo.TableName,
        )

    def createEmbeddingMatchString(self, embeddingInfo, description):
        #vector = embeddingInfo.createEmbedding(data_model)
        #resultdata = list(vector)

        return DapQueryRepn.DapQueryRepn.Leaf(
            operator=OPERATOR_CLOSE_TO,
            query_field_value=description,
            query_field_type="string",
            target_field_name=embeddingInfo.FieldName,
            target_table_name=embeddingInfo.TableName,
        )
