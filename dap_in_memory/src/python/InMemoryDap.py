from typing import Callable
import json

from dap_api.src.protos import dap_description_pb2

from dap_api.src.python import DapInterface
from dap_api.src.python import SubQueryInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.python.DapInterface import decodeConstraintValue
from dap_api.src.python.DapInterface import encodeConstraintValue
from dap_api.src.protos import dap_update_pb2
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.python.DapQueryResult import DapQueryResult
from typing import List
from dap_api.src.python.network.DapNetwork import network_support
from utils.src.python.Logging import has_logger


class InMemoryDap(DapInterface.DapInterface):
    @has_logger

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, configuration):
        self.store = {}
        self.name = name
        self.structure_pb = configuration['structure']
        self.log.update_local_name("InMemoryDap("+name+")")

        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()

        self.tablenames = []
        self.structure = {}
        self.fields = {}

        for table_name, fields in self.structure_pb.items():
            self.tablenames.append(table_name)
            for field_name, field_type in fields.items():
                self.structure.setdefault(table_name, {}).setdefault(field_name, {})['type'] = field_type
                self.fields.setdefault(field_name, {})['tablename']=table_name
                self.fields.setdefault(field_name, {})['type']=field_type

    """This function returns the DAP description which lists the
    tables it hosts, the fields within those tables and the result of
    a lookup on any of those tables.

    Returns:
       DapDescription
    """
    def describe(self) -> dap_description_pb2.DapDescription:
        result = dap_description_pb2.DapDescription()
        result.name = self.name
        result.options.append("leaf-only")

        for table_name, fields in self.structure_pb.items():
            result_table = result.table.add()
            result_table.name = table_name
            for field_name, field_type in fields.items():
                result_field = result_table.field.add()
                result_field.name = field_name
                result_field.type = field_type
        return result

    def processRow(self, rowProcessor, row_key, row, result: dap_interface_pb2.IdentifierSequence):
        core_ident, agent_ident = row_key
        if rowProcessor(row):
            #self.log.info("PASSING: core={}, agent={}".format(core_ident, agent_ident))
            i = result.identifiers.add()
            i.core = core_ident
            i.agent = agent_ident
        else:
            #self.log.info("FAILING: core={}, agent={}".format(core_ident, agent_ident))
            pass

    def processRows(self, rowProcessor, target_table_name, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        #self.log.info("processRows")
        r = dap_interface_pb2.IdentifierSequence()

        table = self.store.get(target_table_name, None)
        if table == None:
            self.log.error("No table {} in {}".format(target_table_name, self.store.keys()))
        else:
            if cores.originator:
                #self.log.info("ORIGINATING")
                for (core_ident, agent_ident), row in table.items():
                    #self.log.info("TESTING ORIGINATED: core={}, agent={}".format(core_ident, agent_ident))
                    self.processRow(rowProcessor, (core_ident, agent_ident), row, r)
            else:
                #self.log.info("SUPPLIED WITH {}".format(len(cores.identifiers)))
                for key in cores.identifiers:
                    core_ident, agent_ident = key.core, key.agent
                    #self.log.info("TESTING SUPPLIED: core={}, agent={}".format(core_ident, agent_ident))
                    row = table.get((core_ident, agent_ident), None)
                    if row == None:
                        self.log.error("{} not found".format((core_ident, agent_ident)))
                        self.log.error("table keys = {}".format(table.keys()))
                    else:
                        self.processRow(rowProcessor, (core_ident, agent_ident), row, r)
        return r

    def runCompareFunc(row, func, target_field_name, query_field_value, log):
        #log.info("runCompareFunc -- target_field_name={}".format(target_field_name))
        #log.info("runCompareFunc -- query_field_value={} {}".format(query_field_value, type(query_field_value)))
        target_field_value = row.get(target_field_name, None)
        #log.info("runCompareFunc -- target_field_value={} {}".format(target_field_value, type(target_field_value)))
        return func(target_field_value, query_field_value)

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        query_settings= json.loads(query_memento.memento.decode("utf-8"))
        #for k,v in query_settings.items():
            #self.log.info(" execute settings    {} = {}".format(k,v))
        try:
            compare_func = self.operatorFactory.lookup(
                query_settings['target_field_type'],
                query_settings['operator'],
                query_settings['query_field_type'])

            #self.info("Function obtained")

            func = lambda row: InMemoryDap.runCompareFunc(
                row,
                compare_func,
                query_settings['target_field_name'],
                query_settings['query_field_value'],
                self.log
                )
            r = self.processRows(func, query_settings['target_table_name'], input_idents)
        except Exception as ex:
            for k,v in query_settings.items():
                self.log.error(" execute settings    {} = {}".format(k,v))
            self.log.error(ex)
            r = dap_interface_pb2.IdentifierSequence()
            r.status.success = False
        return r

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        query_settings = {}
        query_settings['target_table_name'] = proto.target_table_name
        query_settings['target_field_name'] = proto.target_field_name
        query_settings['target_field_type'] = proto.target_field_type
        query_settings['operator'] = proto.operator
        query_settings['query_field_type'] = proto.query_field_type
        query_settings['query_field_value'] = DapInterface.decodeConstraintValue(proto.query_field_value)

        r = dap_interface_pb2.ConstructQueryMementoResponse()
        r.memento = json.dumps(query_settings).encode('utf8')
        r.success = True
        return r

    def print(self):
        print(self.store)

    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    def update(self, tfv: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True

        for commit in [ False, True ]:
            k, v = ProtoHelpers.decodeAttributeValueToTypeValue(tfv.value)
            key = tfv.key
            core_ident, agent_ident = key.core, key.agent
            if tfv.fieldname not in self.fields:
                r.narrative.append("No such field  key={},{} fname={}".format(core_ident, agent_ident, tfv.fieldname))
                r.success = False
                break
            else:
                tbname = self.fields[tfv.fieldname]["tablename"]
                ftype = self.fields[tfv.fieldname]["type"]

            if ftype != k:
                r.narrative.append("Bad Type tname={} key={} fname={} ftype={} vtype={}".format(tbname, upd.key.core, upd.fieldname, ftype, k))
                r.success = False

            if commit:
                self.store.setdefault(tbname, {}).setdefault((core_ident, agent_ident), {})[tfv.fieldname] = v
#                self.log.info("Stored {} into {} for {},{}".format(
#                    tfv.fieldname, tbname, core_ident, agent_ident
#                ))

            if not r.success:
                break
        return r

    def remove(self, remove_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:

        r = dap_interface_pb2.Successfulness()
        r.success = True

        success = False
        for commit in [ False, True ]:
            row_key = (remove_data.key.core, remove_data.key.agent)
            core_ident, agent_ident = row_key
            for tbname in self.store.keys():
                if commit:
                    self.store[tbname].pop(row_key)
            if not r.success:
                break
        return r
