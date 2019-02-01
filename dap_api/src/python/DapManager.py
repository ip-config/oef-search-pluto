import sys
import inspect

from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQuery
from dap_api.src.python import DapQueryRepn

class DapManager(object):
    class PopulateFieldInformationVisitor(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, field_infos):
            self.field_infos = field_infos

        def visitNode(self, node, depth):
            pass

        def visitLeaf(self, node, depth):
            field_info = self.field_infos[node.target_field_name]
            node.target_field_type = field_info['type']
            node.target_table_name = field_info['table']
            node.dap_name = field_info['dap']

    def __init__(self):
        self.instances = {}
        self.operator_factory = DapOperatorFactory.DapOperatorFactory()
        self.structures = {}

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
                    self.structures.setdefault(
                        instance_name, {}).setdefault(
                            table_desc_pb.name, {}).setdefault(
                                field_description_pb.name, {})['type']=field_description_pb.type

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

    def makeQuery(self, query_pb, dapname, tablename):
        dapQuery = DapQuery.DapQuery()
        dap = self.instances[dapname]
        dapQuery.fromQueryProto(query_pb, self.operator_factory, self.structures[dapname][tablename])
        return dapQuery

    def makeQueryRepn(self, query_pb):
        dapQueryRepn = DapQueryRepn.DapQueryRepn()
        dapQueryRepn.fromQueryProto(query_pb)

        # now fill in all the types.

        v = DapManager.PopulateFieldInformationVisitor(self.fields)
        dapQueryRepn.visit(v)
        

        return dapQueryRepn
