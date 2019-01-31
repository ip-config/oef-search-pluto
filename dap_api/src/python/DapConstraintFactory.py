import scipy.spatial.distance as distance


class DapConstraintFactory(object):
    def __init__(self):
        self.store = {}

        self.add("string", "==", "string", lambda a,b: a == b)
        self.add("string", "!=", "string", lambda a,b: a != b)
        self.add("string", "<",  "string", lambda a,b: a < b)
        self.add("string", ">",  "string", lambda a,b: a > b)
        self.add("string", "<=", "string", lambda a,b: a <= b)
        self.add("string", ">=", "string", lambda a,b: a >= b)

        self.add("bool", "==", "bool", lambda a,b: a == b)
        self.add("bool", "!=", "bool", lambda a,b: a != b)

        self.add("location", "==", "location", lambda a,b: a == b)
        self.add("location", "!=", "location", lambda a,b: a != b)

        self.add("embedding", "CLOSETO", "embedding", lambda a,b: self.compareVectors(a,b)) # hack. fix me later. KLL

        self.add("int", "==", "int", lambda a,b: a == b)
        self.add("int", "!=", "int", lambda a,b: a == b)
        self.add("int", "<",  "int", lambda a,b: a == b)
        self.add("int", ">",  "int", lambda a,b: a == b)
        self.add("int", "<=", "int", lambda a,b: a == b)
        self.add("int", ">=", "int", lambda a,b: a >= b)

        self.add("float", "==", "float", lambda a,b: a == b)
        self.add("float", "!=", "float", lambda a,b: a != b)
        self.add("float", "<",  "float", lambda a,b: a < b)
        self.add("float", ">",  "float", lambda a,b: a > b)
        self.add("float", "<=", "float", lambda a,b: a <= b)
        self.add("float", ">=", "float", lambda a,b: a >= b)

        self.add("float",    "IN",    "float_list",    lambda a,b: a in b)
        self.add("float",    "NOTIN", "float_list",    lambda a,b: a not in b)
        self.add("int",      "IN",    "int_list",      lambda a,b: a in b)
        self.add("int"  ,    "NOTIN", "int_list",      lambda a,b: a not in b)
        self.add("string",   "IN",    "string_list",   lambda a,b: a in b)
        self.add("string",   "NOTIN", "string_list",   lambda a,b: a not in b)
        self.add("location", "IN",    "location_list", lambda a,b: a in b)
        self.add("location", "NOTIN", "location_list", lambda a,b: a not in b)

        self.add("float",    "IN", "float_range",    lambda a,b: a > b[0] and a < b[1])
        self.add("int",      "IN", "int_range",      lambda a,b: a > b[0] and a < b[1])
        self.add("string",   "IN", "string_range",   lambda a,b: a > b[0] and a < b[1])
        self.add("location", "IN", "location_range", lambda a,b:
                     a[0] > b[0][0] and a[0] < b[1][0] and
                     a[1] > b[0][1] and a[1] < b[1][1]
                     )

    def compareVectors(self, a, b):
        d = distance.cosine(a,b)
        print("Distance between the two vector: ", d)
        return d < 0.2

    def add(self, field_type, comparator, constant_type, truth_function):
        k = (field_type, comparator, constant_type)
        self.store[k] = truth_function

    def lookup(self, field_type, comparator, constant_type):
        k = (field_type, comparator, constant_type)
        return self.store.get(k, None)

    def processFunc(self, field_value, constant_value, func):
        return func(field_value, constant_value)

    def process(self, field_name, field_type, field_value, comparator, constant_type, constant_value):
        f = self.lookup(field_type, comparator, constant_type)
        if not f:
            raise Exception("{} {} {} {}".format(field_type, comparator, constant_type, " is not known operation."))
        return self.processFunc(field_value, constant_value, f)

    def createAttrMatcherProcessor(self, field_name, field_type, comparator, constant_type, constant_value):
        f = self.lookup(field_type, comparator, constant_type)
        if not f:
            raise BadValue("{} {} {} {}".format(field_type, comparator, constant_type, " is not known operation."))
        return lambda field_value: f(field_value, constant_value)

g_dapConstraintFactory = DapConstraintFactory()

