import utils.src.python.distance as distance
from utils.src.python.Logging import has_logger

from dap_api.src.python import ProtoHelpers

IMPLICIT_TYPE_CONVERSIONS = {
    "int64": "int",
    "int64_list": "int_list",
    "int64_range": "int_range",

    "int32": "int",
    "int32_list": "int_list",
    "int32_range": "int_range",

    "double": "float",
    "double_list": "float_list",
    "double_range": "float_range",
}

class DapOperatorFactory(object):
    @has_logger
    def __init__(self):
        self.store = {}

        self.add("string", ProtoHelpers.OPERATOR_EQ, "string", lambda a,b: a == b)
        self.add("string", ProtoHelpers.OPERATOR_NE, "string", lambda a,b: a != b)
        self.add("string", ProtoHelpers.OPERATOR_LT, "string", lambda a,b: a < b)
        self.add("string", ProtoHelpers.OPERATOR_GT, "string", lambda a,b: a > b)
        self.add("string", ProtoHelpers.OPERATOR_LE, "string", lambda a,b: a <= b)
        self.add("string", ProtoHelpers.OPERATOR_GE, "string", lambda a,b: a >= b)

        self.add("bool", ProtoHelpers.OPERATOR_EQ, "bool", lambda a,b: a == b)
        self.add("bool", ProtoHelpers.OPERATOR_NE, "bool", lambda a,b: a != b)

        self.add("location", ProtoHelpers.OPERATOR_EQ, "location", lambda a,b: a == b)
        self.add("location", ProtoHelpers.OPERATOR_NE, "location", lambda a,b: a != b)

        self.add("int", ProtoHelpers.OPERATOR_EQ, "int", lambda a,b: a == b)
        self.add("int", ProtoHelpers.OPERATOR_NE, "int", lambda a,b: a != b)
        self.add("int", ProtoHelpers.OPERATOR_LT, "int", lambda a,b: a < b)
        self.add("int", ProtoHelpers.OPERATOR_GT, "int", lambda a,b: a > b)
        self.add("int", ProtoHelpers.OPERATOR_LE, "int", lambda a,b: a <= b)
        self.add("int", ProtoHelpers.OPERATOR_GE, "int", lambda a,b: a >= b)

        self.add("float", ProtoHelpers.OPERATOR_EQ, "float", lambda a,b: a == b)
        self.add("float", ProtoHelpers.OPERATOR_NE, "float", lambda a,b: a != b)
        self.add("float", ProtoHelpers.OPERATOR_LT, "float", lambda a,b: a < b)
        self.add("float", ProtoHelpers.OPERATOR_GT, "float", lambda a,b: a > b)
        self.add("float", ProtoHelpers.OPERATOR_LE, "float", lambda a,b: a <= b)
        self.add("float", ProtoHelpers.OPERATOR_GE, "float", lambda a,b: a >= b)

        self.add("float",    ProtoHelpers.OPERATOR_IN,     "float_list",    lambda a,b: a in b)
        self.add("float",    ProtoHelpers.OPERATOR_NOT_IN, "float_list",    lambda a,b: a not in b)
        self.add("int",      ProtoHelpers.OPERATOR_IN,     "int_list",      lambda a,b: a in b)
        self.add("int"  ,    ProtoHelpers.OPERATOR_NOT_IN, "int_list",      lambda a,b: a not in b)
        self.add("string",   ProtoHelpers.OPERATOR_IN,     "string_list",   lambda a,b: a in b)
        self.add("string",   ProtoHelpers.OPERATOR_NOT_IN, "string_list",   lambda a,b: a not in b)
        self.add("location", ProtoHelpers.OPERATOR_IN,     "location_list", lambda a,b: a in b)
        self.add("location", ProtoHelpers.OPERATOR_NOT_IN, "location_list", lambda a,b: a not in b)

        self.add("float",    ProtoHelpers.OPERATOR_IN, "float_range",    lambda a,b: a > b[0] and a < b[1])
        self.add("int",      ProtoHelpers.OPERATOR_IN, "int_range",      lambda a,b: a > b[0] and a < b[1])
        self.add("string",   ProtoHelpers.OPERATOR_IN, "string_range",   lambda a,b: a > b[0] and a < b[1])
        self.add("location", ProtoHelpers.OPERATOR_IN, "location_range", lambda a,b:
                     a[0] > b[0][0] and a[0] < b[1][0] and
                     a[1] > b[0][1] and a[1] < b[1][1]
                     )

    def compareVectors(self, a, b):
        d = distance.cosine(a,b)
        return d < 0.2

    def add(self, field_type, comparator, constant_type, truth_function):
        k = (field_type, comparator, constant_type)
        self.store[k] = truth_function

    def lookup(self, field_type, comparator, constant_type):

        field_type = IMPLICIT_TYPE_CONVERSIONS.get(field_type, field_type)
        constant_type = IMPLICIT_TYPE_CONVERSIONS.get(constant_type,constant_type)

        k = (field_type, comparator, constant_type)
        self.log.info("Operator lookup for: {}".format(k))
        return self.store.get(k, None)
