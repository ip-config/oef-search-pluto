import sys
import inspect

class DapManager(object):
    def __init__(self):
        self.instances = {}

    def setup(self, module, config):
        self.classmakers = self._listClasses(module)

        for k,v in config.items():
            klass_name = v.get('class', v.get('klass', None))
            configuration = v.get('config', None)

            if not klass_name or not configuration:
                raise Exception("{} is not well formed. Requires both 'class' and 'config' objects.".format(k))

            klass = self.classmakers.get(klass_name, None)
            if not klass:
                raise Exception("{} is not well formed. 'class' does't exist.".format(k))
            instance = klass(k, configuration)
            self.instances[k] = instance

            self.fields = self._getFields()

    def _getFields(self):
        r = {} # fieldname -> {dap:$, table:$, type:$)

        for instance_name, instance in self.instances.items():
            structure_pb = instance.describe()

            for table_desc_pb in structure_pb.table:
                for field_description_pb in table_desc_pb.field:
                    r[field_description_pb.name] = {
                        'dap': instance_name,
                        'table': table_desc_pb.name,
                        'type': field_description_pb.type,
                    }

        return r

    def getFields(self):
        return self.fields

    def getInstance(self, name):
        return self.instances[name]

    def _listClasses(self, module):
        r = {}
        for name, obj in inspect.getmembers(module):
            if inspect.ismodule(obj):
                for name, obj in inspect.getmembers(obj):
                    if inspect.isclass(obj):
                        r[name]=obj
            if inspect.isclass(obj):
                r[name]=obj
        return r

#        g = globals().copy()
#    for name, obj in g.items():
#        print(name,obj)

    # We implement this so we can be a DapConstraintFactory
    def process(self, field_name, field_type, field_value, comparator, constant_type, constant_value):
        pass
