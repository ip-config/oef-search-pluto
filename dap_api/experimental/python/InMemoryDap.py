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
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python.DapQueryResult import DapQueryResult
from typing import List
from dap_api.src.python.network.DapNetwork import network_support


class InMemoryDap(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, configuration):
        self.store = {}
        self.name = name
        self.structure_pb = configuration['structure']

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

        for table_name, fields in self.structure_pb.items():
            result_table = result.table.add()
            result_table.name = table_name
            for field_name, field_type in fields.items():
                result_field = result_table.field.add()
                result_field.name = field_name
                result_field.type = field_type
        return result

    def processRows(self, rowProcessor, cores: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        r = dap_interface_pb2.IdentifierSequence()
        for table_name, table in self.store.items():
            if cores.originator:
                for (core_ident, agent_ident), row in table.items():
                    print("TRYING:", core_ident, agent_ident)
                    if rowProcessor(row):
                        print("SUCCESS:", core_ident, agent_ident)
                        i = r.identifiers.add()
                        i.core = core_ident
                        i.agent = agent_ident
            else:
                for key in cores.identifiers:
                    print("KEY=", key.core, key.ident)
                    row = table[(key.core, key.ident)]
                    if rowProcessor(row):
                        i = r.identifiers.add()
                        i.core = core_ident
                        i.agent = agent_ident
        return r


    # returns an object with an execute(agents=None) -> [agent]
    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        return None

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        print("EXECUTE---------------")
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        j = json.loads(query_memento.memento.decode("utf-8"))
        print(j)
        rowProcessor = self.operatorFactory.createAttrMatcherProcessor(
            j['target_field_type'],
            j['operator'],
            j['query_field_type'],
            j['query_field_value'])
        func = lambda row: rowProcessor(row.get(j['target_field_name'], None))

        idents = input_idents
        return self.processRows(func, idents)

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        j = {}
        j['target_field_name'] = proto.target_field_name
        j['target_field_type'] = proto.target_field_type
        j['operator'] = proto.operator
        j['query_field_type'] = proto.query_field_type
        j['query_field_value'] = DapInterface.decodeConstraintValue(proto.query_field_value)

        r = dap_interface_pb2.ConstructQueryMementoResponse()
        r.memento = json.dumps(j).encode('utf8')
        return r

    def print(self):
        print(self.store)

    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    def update(self, update_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True

        for commit in [ False, True ]:
            upd = update_data
            if upd:

                k, v = ProtoHelpers.decodeAttributeValueToTypeValue(upd.value)

                if upd.fieldname not in self.fields:
                    r.narrative.append("No such field  key={} fname={}".format(upd.key, upd.fieldname))
                    r.success = False
                else:
                    tbname = self.fields[upd.fieldname]["tablename"]
                    ftype = self.fields[upd.fieldname]["type"]

                if ftype != k:
                    r.narrative.append("Bad Type tname={} key={} fname={} ftype={} vtype={}".format(tbname, upd.key.core, upd.fieldname, ftype, k))
                    r.success = False

                if commit:
                    self.store.setdefault(tbname, {}).setdefault((upd.key.core, upd.key.agent), {})[upd.fieldname] = v
            if not r.success:
                break

        return r

    def remove(self, remove_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:

        r = dap_interface_pb2.Successfulness()
        r.success = True

        success = False
        for commit in [ False, True ]:
            upd = remove_data
            for tbname in self.store.keys():
                if commit:
                    self.store[tbname].pop(upd.key)
            if not r.success:
                break
        return r
