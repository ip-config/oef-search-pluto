import sys
import inspect
import json

from utils.src.python.Logging import has_logger
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQuery
from dap_api.src.python import DapMatcher
from dap_api.src.python import DapQueryResult
from dap_api.src.python import DapInterface
from dap_api.src.python import DapQueryRepn
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python import SubQueryInterface
from dap_api.src.protos import dap_interface_pb2


class DapManager(object):
    class PopulateFieldInformationVisitor(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, manager):
            self.manager = manager
            self.subn = 1
            self.leaf = 1

        def visitNode(self, node, depth):
            node.name = "node" + str(self.subn)
            self.subn += 1

        def visitLeaf(self, node, depth):
            possible_matchers = self.manager.dap_matchers.items()
            can_matchers = [ (k, v.canMatch(node.target_field_name)) for k,v in possible_matchers ]
            valid_matchers = [ (k,v) for k,v in can_matchers if v != None ]

            node.dap_field_candidates = dict(valid_matchers)
            node.dap_names = set(node.dap_field_candidates.keys())

            node.name = "leaf" + str(self.leaf)
            self.leaf += 1

    class CollectDapsVisitor(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self):
            pass

        def visitNode(self, node, depth):
            node.MergeDaps()

        def visitLeaf(self, node, depth):
            pass


    class NoConstraintCompilerException(Exception):
        def __init__(self, node, dapnames):
            self.node = node
            self.dapnames = dapnames

        def __str__(self):
            return "Node rejected by all daps {}, {}".format(self.dapnames, self.node.printable())

    class PopulateActionsVisitorDescentPass(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, dapmanager):
            self.dapmanager = dapmanager

        def visitNode(self, node, depth):
            for dap_name in node.dap_names or []:
                self.dapmanager.info("Dear ", dap_name, " would you like to consume ", node.printable(), " ?")
                queryObject_pb = self.dapmanager.getInstance(dap_name).prepare(node.toProto(dap_name))
                if queryObject_pb.HasField('success') and queryObject_pb.success:
                    node.memento = queryObject_pb
                    return False
            self.dapmanager.info("Okes, we'll recurse.")
            return True

        def visitLeaf(self, node, depth):
            for dap_name in node.dap_names:
                matcher = node.dap_field_candidates[dap_name]
                self.dapmanager.info("Dear ", dap_name, " would you write a constraint for ", node.printable(), " ?")
                queryObject_pb = self.dapmanager.getInstance(dap_name).prepareConstraint(node.toProto(dap_name))
                if queryObject_pb.HasField('success') and queryObject_pb.success and node.memento == None:
                    node.memento = queryObject_pb
                    node.dap_name = dap_name
            if node.memento == None:
                raise DapManager.NoConstraintCompilerException(node, node.dap_names)


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
        self.log.update_local_name("DapManager")

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

        self.dap_matchers = {}
        self.structures = {}
        self.attributes_to_daps = {}

        for instance_name, instance_object in self.instances.items():
            structure_pb = instance_object.describe()
            self.dap_matchers[instance_name] = DapMatcher.DapMatcher(instance_name, structure_pb)

            for table_desc_pb in structure_pb.table:
                for field_description_pb in table_desc_pb.field:
                    self.structures.setdefault(
                        instance_name, {}).setdefault(
                            table_desc_pb.name, {}).setdefault(
                                field_description_pb.name, {})['type']=field_description_pb.type
                    self.attributes_to_daps.setdefault(field_description_pb.name, []).append(instance_name)

    def getInstance(self, name):
        return self.instances[name]

    def update(self, update: dap_update_pb2.DapUpdate):
        self.info("UPDATE:", self.attributes_to_daps)
        success = True

        if isinstance(update, dap_update_pb2.DapUpdate.TableFieldValue):
            update_list = [ update ]
        else:
            update_list = update.update

        for tableFieldValue in update_list:
            daps_to_update = self.attributes_to_daps.get(tableFieldValue.fieldname, []) + self.attributes_to_daps.get('*', [])
            for dap_to_update in daps_to_update:
                self.info("UPDATE ", tableFieldValue.key.core, tableFieldValue.key.agent, " -> ", dap_to_update)
                r = self.getInstance(dap_to_update).update(tableFieldValue)
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

    def printQuery(self, prefix, dapQueryRepn):
        for x in dapQueryRepn.printable():
            self.info("{}   {}".format(prefix, x))

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

        v = DapManager.PopulateFieldInformationVisitor(self)
        dapQueryRepn.visit(v)
        self.printQuery("FIELD_INFO_PASS ", dapQueryRepn)

        v = DapManager.CollectDapsVisitor()
        dapQueryRepn.visit(v)
        self.printQuery("COLLECT_PASS    ", dapQueryRepn)

        return dapQueryRepn

    def execute(self, dapQueryRepn) -> dap_interface_pb2.IdentifierSequence:

        self.printQuery("EXECUTE         ", dapQueryRepn)

        v1 = DapManager.PopulateActionsVisitorDescentPass(self)
        try:
            dapQueryRepn.visitDescending(v1)
        except DapManager.NoConstraintCompilerException as ex:
            r = dap_interface_pb2.IdentifierSequence()
            failure = r.status
            failure.success = False
            failure.narrative.append(str(ex))
            return r
        self.printQuery("GEN_ACTIONS_PASS", dapQueryRepn)

        start = dap_interface_pb2.IdentifierSequence()
        start.originator = True
        return self._execute(dapQueryRepn.root, start)

    def _execute(self, node, cores) -> dap_interface_pb2.IdentifierSequence:
        if node.memento:
            proto = dap_interface_pb2.DapExecute()
            proto.query_memento.CopyFrom(node.memento)
            proto.input_idents.CopyFrom(cores)
            r = self.getInstance(list(node.dap_names)[0]).execute(proto)
        elif node.combiner == "any":
            r = self._executeOr(node, cores)
        elif node.combiner == "all":
            r = self._executeAnd(node, cores)
        else:
            raise Exception("Node combiner '{}' not handled.".format(node.combiner))
#        print("_executeNode")
#        print("Results;")
#        for ident in r.identifiers:
#            print(DapQueryResult.DapQueryResult(pb=ident).printable())
        return r

    def _executeLeaf(self, node, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        if node.memento:
            proto = dap_interface_pb2.DapExecute()
            proto.query_memento.CopyFrom(node.memento)
            proto.input_idents.CopyFrom(cores)
            results = self.getInstance(node.dap_name).execute(proto)
            r = results
        else:
            raise Exception("Node didn't compile")
#        print("_executeLeaf")
#        print("Results;")
#        for ident in r.identifiers:
#            print(DapQueryResult.DapQueryResult(pb=ident).printable())
        return r

    def _executeOr(self, node, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        r = dap_interface_pb2.IdentifierSequence()
        for n in node.subnodes:
            res = self._execute(n, cores)
            for ident in res.identifiers:
                newid = r.identifiers.add()
                newid.CopyFrom(ident)
        for n in node.leaves:
            res = self._executeLeaf(n, cores)
            for ident in res.identifiers:
                newid = r.identifiers.add()
                newid.CopyFrom(ident)
        return r

    # This is naive -- there's a functional way of making this more efficient.
    def _executeAnd(self, node, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        leafstart = 0
        nodestart = 0

        for n in node.leaves[leafstart:]:
            cores = self._executeLeaf(n, cores)
            if len(cores.identifiers) == 0:
                return dap_interface_pb2.IdentifierSequence()

        for n in node.subnodes[nodestart:]:
            cores = self._execute(n, cores)
            if len(cores.identifiers) == 0:
                return dap_interface_pb2.IdentifierSequence()

        return cores

    # passing in the embedding system is part of the hack SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
    def setDataModelEmbedder(self, embedderName, embeddingTableName, embeddingFieldName):
        self.embedderName = embedderName
        self.embeddingTableName = embeddingTableName
        self.embeddingFieldName = embeddingFieldName
