import sys
import inspect
import json

from utils.src.python.Logging import has_logger
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQuery
from dap_api.src.python import DapQueryResult
from dap_api.src.python import DapInterface
from dap_api.src.python import DapQueryRepn
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python import SubQueryInterface
from dap_api.src.protos import dap_interface_pb2


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
                #print("Hello " + node.common_dap_name + ". Would you like to consume " + node.printable())

                queryObject_pb = self.dapmanager.getInstance(node.common_dap_name).prepare(node.toProto())
                if queryObject_pb.HasField('success') and queryObject_pb.success:
                    node.memento = queryObject_pb.memento
                    return False
            #print("Okes, we'll recurse.")
            return True

        def visitLeaf(self, node, depth):
            pb = node.toProto()
            node.memento = self.dapmanager.getInstance(node.dap_name).prepareConstraint(pb)

    # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
    class EmbeddingInfo(object):
        def __init__(self):
            self.dapName = None
            self.embeddingDap = None
            self.FieldName = None
            self.TableName = None

    @has_logger
    def __init__(self):
        self.instances = {}
        self.operator_factory = DapOperatorFactory.DapOperatorFactory()
        self.structures = {}
        self.embedderName = None  # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        self.embeddingFieldName = None # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        self.embeddingTableName = None # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        self.classmakers = {}

    def addClass(self, name, maker):
        self.classmakers[name] = maker

    def setup(self, module, config):
        self.classmakers.update(self._listClasses(module))

        if module==None or config==None:
            raise Exception("need a module and config")

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

    def getField(self, fieldname):
        return self.fields.get(fieldname, None)

    def getInstance(self, name):
        return self.instances[name]

    def update(self, update: dap_update_pb2.DapUpdate):
        success = True
        for upd in update.update:
            cls = self.getField(upd.fieldname)["dap"]
            r = self.getInstance(cls).update(upd)
            if r.success == False:
                for m in r.narrative:
                    self.log.error(m)
            success &= r.success
        return success

    def remove(self, remove: dap_update_pb2.DapUpdate):
        success = True
        for upd in remove.update:
            cls = self.getField(upd.fieldname)["dap"]
            r = self.getInstance(cls).remove(upd)
            if r.success == False:
                for m in r.narrative:
                    self.log.error(m)
            success &= r.success
        return success

    def removeAll(self, key):
        success = True
        update = dap_update_pb2.DapUpdate()
        update.update.add().key = key
        for instance in self.instances:
            r = instance.remove(update)
            if r.success == False:
                for m in r.narrative:
                    self.log.error(m)
            success &= r.success
        return success

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

        embeddingInfo = DapManager.EmbeddingInfo()

        # passing in the embedding system is part of the hack SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        embeddingInfo.dapName = self.embedderName
        embeddingInfo.embeddingDap = self.instances.get(embeddingInfo.dapName, None)
        embeddingInfo.FieldName = self.embeddingFieldName
        embeddingInfo.TableName = self.embeddingTableName

        if not embeddingInfo.embeddingDap:
            embeddingInfo = None

        dapQueryRepn.fromQueryProto(query_pb, embeddingInfo)

        # now fill in all the types.
        v = DapManager.PopulateFieldInformationVisitor(self.fields)
        dapQueryRepn.visit(v)

        v = DapManager.CollectDapsVisitor(self.fields)
        dapQueryRepn.visit(v)

        return dapQueryRepn

    def makeQueryFromConstraintProto(self, query_pb):
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

    def _execute(self, node, cores=None):
        if node.combiner == "any":
            yield from self._executeOr(node, cores)
        elif node.combiner == "all":
            yield from self._executeAnd(node, cores)
        else:
            raise Exception("Node combiner '{}' not handled.".format(node.combiner))

    def _executeLeaf(self, node, cores=None):
        if node.query:
            yield from node.query.execute(cores)
        elif node.memento:
            proto = dap_interface_pb2.DapExecute()
            proto.query_memento.CopyFrom(node.memento)
            proto.input_idents.CopyFrom(DapInterface.coresToIdentifierSequence(cores))
            results = self.getInstance(node.dap_name).execute(proto)
            for identifier in results.identifiers:
                yield DapQueryResult.DapQueryResult(identifier.core)
        else:
            raise Exception("Node didn't compile")

    def _executeOr(self, node, cores=None):
        for n in node.subnodes:
            yield from self._execute(n, cores)
        for n in node.leaves:
            yield from self._executeLeaf(n, cores)

    # This is naive -- there's a functional way of making this more efficient.
    def _executeAnd(self, node, cores=None):
        leafstart = 0
        nodestart = 0

        if cores is None:
            if len(node.leaves) > 0:
                cores = list(self._executeLeaf(node.leaves[0]))
                leafstart = 1

        if cores is None:
            if len(node.subnodes) > 0:
                cores = self._execute(node.subnodes[0])
                nodestart = 1

        if cores is None or cores == []:
            return []

        cores = list(cores)
        for n in node.leaves[leafstart:]:
            cores = list(self._executeLeaf(n, cores))
            if len(cores) == 0:
                return []

        for n in node.subnodes[nodestart:]:
            cores = list(self._execute(n, cores))
            if len(cores) == 0:
                return []

        return cores

    # passing in the embedding system is part of the hack SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
    def setDataModelEmbedder(self, embedderName, embeddingTableName, embeddingFieldName):
        self.embedderName = embedderName
        self.embeddingTableName = embeddingTableName
        self.embeddingFieldName = embeddingFieldName
