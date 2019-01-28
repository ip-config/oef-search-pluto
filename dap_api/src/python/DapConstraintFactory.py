

class DapConstraintFactory(object):
    def __init__(self):
        self.store = {}

        self.add("string", "==", "string", lambda a,b: a == b)
        self.add("string", "!=", "string", lambda a,b: a != b)
        self.add("string", "<",  "string", lambda a,b: a < b)
        self.add("string", ">",  "string", lambda a,b: a > b)
        self.add("string", "<=", "string", lambda a,b: a <= b)
        self.add("string", ">=", "string", lambda a,b: a >= b)

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

    def add(self, field_type, comparator, constant_type, truth_function):
        k = (field_type, comparator, constant_type)
        self.store[k] = truth_function

    def lookup(self, field_type, comparator, constant_type):
        k = (field_type, comparator, constant_type)
        return self.store.get(k, None)

    def processFunc(self, field_value, constant_value, func):
        return func(field_value, constant_value)

    def process(self, field_type, field_value, comparator, constant_type, constant_value):
        f = self.lookup(field_type, comparator, constant_type)
        if not f:
            raise BadValue("{} {} {} {}".format(field_type, comparator, constant_type, " is not known operation."))
        return self.processFunc(field_value, constant_value, f)

g_dapConstraintFactory = DapConstraintFactory()

