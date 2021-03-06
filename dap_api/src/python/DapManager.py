import sys
import inspect
import json
import re
import copy
import time
import subprocess
import socket
import atexit

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
from dap_api.src.protos import dap_update_pb2


def dap_json_from_config(name, config):
    new_config = {
        "host": config["host"],
        "port": config["port"],
        "description": {
            "name": name
        }
    }
    desc = new_config["description"]
    desc["table"] = []
    for tb_name, fields in config["structure"].items():
        t = {
            "name": tb_name,
            "field": [
                {
                    "name": field_name,
                    "type": field_type
                } for field_name, field_type in fields.items()
            ]
        }
        desc["table"].append(t)
    return json.dumps(new_config)


def create_dap_process(logger, name: str, config: dict, exe_dir: str, log_dir: str):
    exe = config["binary"]
    json_config = dap_json_from_config(name, config)
    if len(exe_dir) == 0:
        logger.warning("No exe_dir set! Can't run C++ dap without it!")
        return None
    logger.info("*********** BINARY DAP EXECUTION DIR: %s", exe_dir)
    logger.warning("*********** RUN DAP: %s  with the following config: %s", exe, json_config)
    cmd = [
        exe,
        "--configjson",
        json_config,
    ]
    if len(log_dir) == 0:
        remoteProcess = subprocess.Popen(cmd, cwd=exe_dir)
    else:
        log_file = open(log_dir+"/"+name+".log", "w")
        remoteProcess = subprocess.Popen(cmd, cwd=exe_dir, stdout=log_file, stderr=log_file)
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((config["host"], config["port"])) != 0:
            time.sleep(0.5)
            print(".")
        else:
            logger.info("DAP %s @ %s:%d started, port open!", exe, config["host"], config["port"])
            break
    return remoteProcess


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
            matching_daps = self.manager.getDapsForAttributeName(node.target_field_name)
            matching_daps_and_configs = [
                (k, self.manager.dap_matchers.get(k, None) )
                for k
                in matching_daps
            ]
            matching_daps_and_configuration_outputs = [
                (k, v.canMatch(node.target_field_name) if v else {} )
                for k,v in matching_daps_and_configs
            ]
            null_safed_matching_daps_and_configuration_outputs = [
                (k, v if v != None else {} )
                for k,v in matching_daps_and_configuration_outputs
            ]

            node.dap_field_candidates = dict(null_safed_matching_daps_and_configuration_outputs)
            node.dap_names = set(node.dap_field_candidates.keys())
            node.name = "leaf" + str(self.leaf)
            self.leaf += 1

    class AddMoreDapsBasedOnOptionsVisitor(DapQueryRepn.DapQueryRepn.Visitor):
        def __init__(self, manager):
            self.manager = manager

        def visitNode(self, node, depth):
            for dap in self.manager.getDapNamesByOptions('all-branches', 'all-nodes'):
                if node.dap_names == None or dap not in node.dap_names:
                    node.dap_names = node.dap_names or set()
                    node.dap_names.add(dap)
                    node.dap_field_candidates[dap] = {}

        def visitLeaf(self, node, depth):
            for dap in self.manager.getDapNamesByOptions('all-leaf', 'all-nodes'):
                if node.dap_names == None or dap not in node.dap_names:
                    node.dap_names = node.dap_names or set()
                    node.dap_names.add(dap)
                    node.dap_field_candidates[dap] = {}

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
                    node.mementos.extend([
                        (dap_name, queryObject_pb)
                    ])
                    self.dapmanager.info("Gotcha ", dap_name, " node now at ", node.printable())
                    if self.dapmanager.isDap(dap_name, "late"):
                        continue
                    else:
                        return False
            self.dapmanager.info("Okes, we'll recurse.")
            return True

        def visitLeaf(self, node, depth):
            for dap_name in node.dap_names:
                self.dapmanager.info("Dear ", dap_name, " would you write a constraint for ", node.printable(), " ?")
                queryObject_pb = self.dapmanager.getInstance(dap_name).prepareConstraint(node.toProto(dap_name))
                if queryObject_pb.HasField('success') and queryObject_pb.success:
                    self.dapmanager.info("Gotcha!")
                    node.mementos.extend([
                        (dap_name, queryObject_pb)
                    ])
            if len(node.mementos) == 0:
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
        self.dap_options = {}
        self.embedderName = None  # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        self.embeddingFieldName = None # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        self.embeddingTableName = None # SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
        self.classmakers = {}
        self.log.update_local_name("DapManager")
        self.planes = {}
        self.dap_processes = []

    def addClass(self, name, maker):
        self.classmakers[name] = maker

    def _process_cleaner(self):
        self.error("Cleaning DAP processes!")
        for proc in self.dap_processes:
            if proc is not None:
                proc.kill()

    def setup(self, module, config, exe_dir="", log_dir=""):
        self.classmakers.update(self._listClasses(module))
        atexit.register(DapManager._process_cleaner, self)

        if module==None or config==None:
            raise Exception("need a module and config")

        for k,v in config.items():
            klass_name = v.get('class', v.get('klass', None))
            configuration = v.get('config', None)

            if not klass_name or not configuration:
                raise Exception("{} is not well formed. Requires both 'class' and 'config' objects.".format(k))

            if klass_name.find("exe.") != -1:
                # its a binary dap, we need to run it and create a proxy
                process_config = copy.deepcopy(configuration)
                self.dap_processes.append(create_dap_process(self.log, klass_name, process_config, exe_dir, log_dir))
                klass_name = "DapNetworkProxy"

            klass = self.classmakers.get(klass_name, None)
            if not klass:
                raise Exception("{} is not well formed (klass_name={}). 'class' does't exist.".format(k, klass_name))
            instance = klass(k, configuration)
            self.instances[k] = instance

        self.dap_matchers = {}
        self.structures = {}
        self.attributes_to_dapnames = {}

        for instance_name, instance_object in self.instances.items():
            self.warning("INTERROGATE:" + str(type(instance_object)))
            structure_pb = instance_object.describe()

            self.warning("INTERROGATE:" + instance_name + " Returned a description: " + str(structure_pb))

            self.dap_matchers[instance_name] = DapMatcher.DapMatcher(instance_name, structure_pb)
            self.dap_options[instance_name] = set(structure_pb.options)

            self.warning(instance_name + " Returned a options: " + str(structure_pb.options))

            for table_desc_pb in structure_pb.table:
                self.warning(instance_name + " Returned a description for table ", table_desc_pb.name)
                for field_description_pb in table_desc_pb.field:
                    self.structures.setdefault(
                        instance_name, {}).setdefault(
                            table_desc_pb.name, {}).setdefault(
                                field_description_pb.name, {})['type']=field_description_pb.type
                    if 'plane' in field_description_pb.options:
                        self.planes[field_description_pb.type] = {
                            'dap_name': instance_name,
                            'table_name': table_desc_pb.name,
                            'field_name': field_description_pb.name,
                            'field_type': field_description_pb.type,
                        }
                    self.attributes_to_dapnames.setdefault(field_description_pb.name, []).append(instance_name)

    def getInstance(self, name):
        return self.instances[name]

    def getPlaneInformation(self, name):
        r = self.planes.get(name, None)
        store = self.getInstance(r.get('dap_name', '')) or object()
        if hasattr(store, 'listCores'):
            r['values'] = list(store.listCores(r['table_name'], r['field_name']))
        return r

    def matchAttributeName(self, pattern, attributeName):
        if pattern == '*':
            self.log.info("getDapsForAttributeName YES because {} == *".format(pattern))
            return True
        if pattern[0] == '/' and pattern[-1:] == '/':
            pat = pattern[1:-1]
            if re.match('^'+pat+'$', attributeName):
                self.log.info("getDapsForAttributeName YES because {}  matches {} ".format(pat, attributeName))
                return True
        if pattern == attributeName:
            self.log.info("getDapsForAttributeName YES because {} == {} ".format(pattern, attributeName))
            return True
        return False

    def getDapsForAttributeName(self, attributeName):
        r = set()
        for attribute_name, dap_filter in [
            (
                attributeName,
                lambda x: True,
            ),
            (
                "them." + attributeName,
                lambda dap: not self.isDap(dap, 'lazy'),
            ),
            (
                "them." + attributeName,
                lambda dap: len(r)==0 and self.isDap(dap, 'lazy'),
            ),
        ]:
            for attribute_pattern, dapnames in self.attributes_to_dapnames.items():
                self.log.info("TRYING: {} {}".format(attribute_name, attribute_pattern, dapnames))
                if not self.matchAttributeName(attribute_pattern, attribute_name):
                    continue
                newdaps = set()
                for dap in dapnames:
                    self.log.info("getDapsForAttributeName considering {}".format(dap))
                    if dap_filter(dap):
                        newdaps.add(dap)
                r |= newdaps
        self.log.error("getDapsForAttributeName {} => {}".format(attributeName, r))
        return r

    def isDap(self, dapName, *attributes):
        return len(self.dap_options.get(dapName, set()).intersection(attributes))

    def getDapNamesByOptions(self, *attributes):
        return [
            instance_name
            for instance_name, options
            in self.dap_options.items()
            if options.intersection(attributes)
        ]

    def isDapEarly(self, dapName):
        return self.isDap(dapName, 'early')

    def isDapLate(self, dapName):
        return self.isDap(dapName, 'late')

    def update(self, update: dap_update_pb2.DapUpdate):
        success = True
        if isinstance(update, dap_update_pb2.DapUpdate.TableFieldValue):
            update_list = [ update ]
        else:
            update_list = update.update

        for tableFieldValue in update_list:
            daps_to_update = self.getDapsForAttributeName(tableFieldValue.fieldname)

            if len(daps_to_update) == 0:
                self.log.error("NO DAPS CLAIMED THIS VALUE -- {}".format(tableFieldValue.fieldname))
                success = False

            for dap_to_update in daps_to_update:
                tfv = dap_update_pb2.DapUpdate.TableFieldValue()
                tfv.CopyFrom(tableFieldValue)
                r = self.getInstance(dap_to_update).update(tfv)
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
            self.log.info("{}   {}".format(prefix, x))

    def makeQueryFromConstraint(self, query_constraint_pb):
        dapQueryRepn = DapQueryRepn.DapQueryRepn()
        dapQueryRepn.fromConstraintProtoList(None, [ query_constraint_pb ])

        # now fill in all the types.

        v = DapManager.PopulateFieldInformationVisitor(self)
        dapQueryRepn.visit(v)
        self.printQuery("FIELD_INFO_PASS ", dapQueryRepn)

        v = DapManager.CollectDapsVisitor()
        dapQueryRepn.visit(v)
        self.printQuery("COLLECT_PASS    ", dapQueryRepn)

        v = DapManager.AddMoreDapsBasedOnOptionsVisitor(self)
        dapQueryRepn.visit(v)
        self.printQuery("EXTRA_DAPS_PASS ", dapQueryRepn)

        return dapQueryRepn

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

        v = DapManager.AddMoreDapsBasedOnOptionsVisitor(self)
        dapQueryRepn.visit(v)
        self.printQuery("EXTRA_DAPS_PASS ", dapQueryRepn)

        return dapQueryRepn

    def execute(self, dapQueryRepn) -> dap_interface_pb2.IdentifierSequence:

        self.printQuery("EXECUTE         ", dapQueryRepn)

        v1 = DapManager.PopulateActionsVisitorDescentPass(self)
        try:
            dapQueryRepn.visitDescending(v1)
        except DapManager.NoConstraintCompilerException as ex:
            r = dap_interface_pb2.IdentifierSequence()
            r.originator = False
            failure = r.status
            failure.success = False
            failure.narrative.append(str(ex))
            return r

        self.printQuery("GEN_ACTIONS_PASS", dapQueryRepn)
        start = dap_interface_pb2.IdentifierSequence()
        start.originator = True
        return self._execute(dapQueryRepn.root, start)

    def _execute(self, node, cores) -> dap_interface_pb2.IdentifierSequence:

        early_daps = []
        regular_daps = []
        late_daps = []
        for dap_name, memento in node.mementos:
            if self.isDapEarly(dap_name):
                early_daps.append( (dap_name, memento) )
            elif self.isDapLate(dap_name):
                late_daps.append( (dap_name, memento) )
            else:
                regular_daps.append( (dap_name, memento) )

        if early_daps + regular_daps:
            r = self._executeMementoChain(node, early_daps + regular_daps, cores)
        else:
            if node.combiner == "any":
                r = self._executeOr(node, cores)
            elif node.combiner == "result":
                r = self._executeAnd(node, cores)
            elif node.combiner == "all":
                r = self._executeAnd(node, cores)
            else:
                raise Exception("Node combiner '{}' not handled.".format(node.combiner))

        if late_daps:
            r = self._executeMementoChain(node, late_daps, r)

#        print("_executeNode")
#        print("Results;")
        return r

    def _executeMementoChain(self, node, ordered_mementos, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        self.warning("_executeMementoChain working on ", node.printable())
        self.warning("_executeMementoChain will run: ", [ m[0] for m in ordered_mementos ])
        self.warning("_executeMementoChain input count ", len(cores.identifiers))
        try:
            current = cores
            for dap_name, memento in ordered_mementos:
                try:
                    proto = dap_interface_pb2.DapExecute()
                    proto.query_memento.CopyFrom(memento)
                    proto.input_idents.CopyFrom(current)
                    current = self.getInstance(dap_name).execute(proto)
                except Exception as e:
                    self.exception("_executeMementoChain error: {} dapname={}".format(str(e), dap_name))
                    raise e
        except Exception as e:
            self.error("_executeMementoChain error: ", str(e))
        self.warning("_executeMementoChain output count ", len(current.identifiers))
        return current

    def _executeLeaf(self, node, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        self.warning("_executeLeaf working on ", node.printable())
        if len(node.mementos) > 0:
            r = self._executeMementoChain(node, node.mementos, cores)
        else:
            raise Exception("Node didn't compile")
        #self.log.info("_executeLeaf")
        #self.log.info("Results;")
        #for ident in r.identifiers:
        #    self.log.info(DapQueryResult.DapQueryResult(pb=ident).printable())
        return r

    def _executeOr(self, node, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        self.warning("_executeOr ", node.printable())
        r = dap_interface_pb2.IdentifierSequence()
        r.originator = False
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
        self.warning("_executeAnd ", node.printable())
        leafstart = 0
        nodestart = 0

        for n in node.leaves[leafstart:]:
            cores = self._executeLeaf(n, cores)
            if len(cores.identifiers) == 0:
                result = dap_interface_pb2.IdentifierSequence()
                result.originator = False
                return result

        for n in node.subnodes[nodestart:]:
            cores = self._execute(n, cores)
            if len(cores.identifiers) == 0:
                result = dap_interface_pb2.IdentifierSequence()
                result.originator = False
                return result

        return cores

    # passing in the embedding system is part of the hack SUPPORT_SINGLE_GLOBAL_EMBEDDING_QUERY
    def setDataModelEmbedder(self, embedderName, embeddingTableName, embeddingFieldName):
        self.embedderName = embedderName
        self.embeddingTableName = embeddingTableName
        self.embeddingFieldName = embeddingFieldName
