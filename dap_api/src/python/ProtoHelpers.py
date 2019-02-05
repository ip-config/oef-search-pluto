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

OPERATOR_EQ = "=="
OPERATOR_NE = "!="
OPERATOR_LE = "<="
OPERATOR_GE = ">="
OPERATOR_LT = "<"
OPERATOR_GT = ">"
OPERATOR_CLOSE_TO = "CLOSE_TO"
OPERATOR_IN = "IN"
OPERATOR_NOT_IN = "NOTIN"

def listOf(x)
    return("{}_list".format(x))

def rangeOf(x)
    return("{}_range".format(x))

def decodeTableFieldValue(tfv):
    type =
    {
        0: None,
        1: None,
        2: TYPE_STRING,
        3: TYPE_INT64,
        4: TYPE_FLOAT,
        5: TYPE_DOUBLE,
        6: TYPE_DATA_MODEL,
        7: TYPE_EMBEDDING,
    }[tfv.value.type]
    return (tfv.tablename, tfv.fieldname, tfv.type)
