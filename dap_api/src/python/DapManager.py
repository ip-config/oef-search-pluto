import sys
import inspect

from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQuery
from dap_api.src.python import DapQueryRepn

class DapManager(object):
    class PopulateFieldInformationVisitor(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, field_infos):
            self.field_infos = field_infos
            self.subn = 1
            self.leaf = 1

        def visitNode(self, node, depth):
            node.query = None
            node.name = "node" + str(self.subn)
            self.subn += 1

        def visitLeaf(self, node, depth):
            field_info = self.field_infos[node.target_field_name]
            node.target_field_type = field_info['type']
            node.target_table_name = field_info['table']
            node.dap_name = field_info['dap']
            node.name = "leaf" + str(self.leaf)
            self.leaf += 1

    class CollectDapsVisitor(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, field_infos):
            pass

        def visitNode(self, node, depth):
            node.MergeDaps()

        def visitLeaf(self, node, depth):
            pass

    class PopulateActionsVisitorDescentPass(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, dapmanager):
            self.dapmanager = dapmanager

        def visitNode(self, node, depth):
            if node.common_dap_name:
                queryObject = self.dapmanager.getInstance(node.common_dap_name).constructQueryObject(node)
                if queryObject:
                    node.query = queryObject
                    return False
            return True

        def visitLeaf(self, node, depth):
            node.query = self.dapmanager.getInstance(node.dap_name).constructQueryConstraintObject(node)

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

    def makeQuery(self, query_pb):
        dapQueryRepn = DapQueryRepn.DapQueryRepn()
        dapQueryRepn.fromQueryProto(query_pb)

        # now fill in all the types.
        v = DapManager.PopulateFieldInformationVisitor(self.fields)
        dapQueryRepn.visit(v)

        v = DapManager.CollectDapsVisitor(self.fields)
        dapQueryRepn.visit(v)

        return dapQueryRepn

    def execute(self, dapQueryRepn):
        v1 = DapManager.PopulateActionsVisitorDescentPass(self)
        dapQueryRepn.visitDescending(v1)
        return list(self._execute(dapQueryRepn.root))

    def _execute(self, node, agents=None):
        if node.query:
            yield from node.query.execute(agents)
        elif node.combiner == "any":
            yield from self._executeOr(node, agents)
        elif node.combiner == "all":
            yield from self._executeAnd(node, agents)
        else:
            raise Exception("Node combiner '{}' not handled.".format(node.combiner))

    def _executeOr(self, node, agents=None):
        for n in node.subnodes:
            yield from self._execute(n, agents)
        for n in node.leaves:
            yield from n.query.execute()

    # This is naive -- there's a functional way of making this more efficient.
    def _executeAnd(self, node, agents=None):
        if agents == None:
            if len(node.leaves) > 0:
                agents = list(node.leaves[0].query.execute())

        if agents == None:
            if len(node.subnodes) > 0:
                agents = self._execute(node.subnodes[0])

        if agents == None or agents == []:
            return []


        agents = list(agents)
        for n in node.leaves:
            agents = list(n.query.execute(agents))
            if len(agents) == 0:
                return []

        for n in node.subnodes:
            agents = list(self._execute(n, agents))
            if len(agents) == 0:
                return []

        return agents

