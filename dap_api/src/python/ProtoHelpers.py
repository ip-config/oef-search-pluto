from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2

TYPE_STRING = "string"
TYPE_DATA_MODEL = "dm"
TYPE_EMBEDDING = "embedding"
TYPE_INT32 = "int32"
TYPE_INT64 = "int64"
TYPE_FLOAT = "float"
TYPE_DOUBLE = "double"
TYPE_BOOL = "bool"
TYPE_LOCATION = "location"
TYPE_ADDRESS = "address"

OPERATOR_EQ = "=="
OPERATOR_NE = "!="
OPERATOR_LE = "<="
OPERATOR_GE = ">="
OPERATOR_LT = "<"
OPERATOR_GT = ">"
OPERATOR_CLOSE_TO = "CLOSE_TO"
OPERATOR_IN = "IN"
OPERATOR_NOT_IN = "NOTIN"

COMBINER_ALL = "all"
COMBINER_ANY = "any"
COMBINER_NONE = "none"

def listOf(x):
    return("{}_list".format(x))


def rangeOf(x):
    return("{}_range".format(x))


def decodeAttributeValueToInfo(av):
    return {
        0: ( None, lambda x: None),
        1: ( None, lambda x: None),
        2: ( TYPE_STRING,lambda x: x.s),
        3: ( TYPE_INT64,lambda x: x.s),
        4: ( TYPE_FLOAT,lambda x: x.i),
        5: ( TYPE_DOUBLE,lambda x: x.d),
        6: ( TYPE_DATA_MODEL, lambda x: x.dm), # not impl yet
        7: ( TYPE_INT32,lambda x: x.i32),
        8: ( TYPE_BOOL,lambda x: x.b),
        9: ( TYPE_LOCATION,lambda x: x.l),
        10: (TYPE_ADDRESS, lambda x: x.a)
    }.get(av.type, ( None, lambda x: None))


def decodeAttributeValueToTypeValue(av):
    t, func = decodeAttributeValueToInfo(av)
    v = func(av)
    return t, v


def decodeAttributeValueToType(av):
    return decodeAttributeValueToInfo(av)[0]
