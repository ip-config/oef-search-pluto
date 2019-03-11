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
from dap_api.src.protos import dap_interface_pb2 as dap_interface
from dap_api.src.python.DapQueryResult import DapQueryResult
from typing import List


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
    def describe(self):
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

    def processRows(self, rowProcessor, cores: List[DapQueryResult] = None):
        for table_name, table in self.store.items():
            if cores is None:
                for key, row in table.items():
                    if rowProcessor(row):
                        yield DapQueryResult(key)
            else:
                for key in cores:
                    print("KEY=", key)
                    row = table[key()]
                    if rowProcessor(row):
                        yield key


    # returns an object with an execute(agents=None) -> [agent]
    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        return None

    # class ConstraintProcessor(SubQueryInterface.SubQueryInterface):
    #     NAMES = [
    #         "target_field_type",
    #         "operator",
    #         "query_field_type",
    #         "query_field_value",
    #     ]
        
    #     def __init__(self):
    #         pass

    #     def fromLeaf(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf):
    #         self.values = {}
    #         for k in ConstraintProcessor.NAMES:
    #             values[k] = getattr(dapQueryRepnLeaf, k)

    #     def toProto(self):
    #         self.

    #     def execute(self, agents=None):
    #         rowProcessor = self.operatorFactory.createAttrMatcherProcessor(
    #             self.values['target_field_type'],
    #             self.values['operator'],
    #             self.values['query_field_type'],
    #             self.values['query_field_value'])
    #         self.func = lambda row: rowProcessor(row.get(self.values['target_field_name'], None))

    #     InMemoryDap.ConstraintProcessor(self, rowProcessor, dapQueryRepnLeaf.target_field_name)
    #         yield from self.inMemoryDap.processRows(func, agents)


    def execute(self, proto: dap_interface.ConstructQueryMementoResponse, input_idents: dap_interface.IdentifierSequence) -> dap_interface.IdentifierSequence:
        print("EXECUTE---------------")
        j = json.loads(proto.memento.decode("utf-8"))
        rowProcessor = self.operatorFactory.createAttrMatcherProcessor(
            j['target_field_type'],
            j['operator'],
            j['query_field_type'],
            j['query_field_value'])
        func = lambda row: rowProcessor(row.get(j['target_field_name'], None))

        if input_idents.HasField('originator') and input_idents.originator:
            idents = None
        else:
            idents = [ DapQueryResult(x) for x in input_idents.identifiers ]

        reply = dap_interface.IdentifierSequence()
        reply.originator = False;
        for core in self.processRows(func, idents):
            c = reply.identifiers.add()
            c.core = core()
        return reply

    def prepareConstraint(self, proto: dap_interface.ConstructQueryConstraintObjectRequest) -> dap_interface.ConstructQueryMementoResponse:
        j = {}
        j['target_field_name'] = proto.target_field_name
        j['target_field_type'] = proto.target_field_type
        j['operator'] = proto.operator
        j['query_field_type'] = proto.query_field_type
        j['query_field_value'] = DapInterface.decodeConstraintValue(proto.query_field_value)

        r = dap_interface.ConstructQueryMementoResponse()
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
    def update(self, update_data: dap_update_pb2.DapUpdate.TableFieldValue):
        for commit in [ False, True ]:
            upd = update_data
            if upd:

                k, v = ProtoHelpers.decodeAttributeValueToTypeValue(upd.value)

                if upd.fieldname not in self.fields:
                    raise DapBadUpdateRow("No such field", None, upd.key, upd.fieldname, k)
                else:
                    tbname = self.fields[upd.fieldname]["tablename"]
                    ftype = self.fields[upd.fieldname]["type"]

                if ftype != k:
                    raise DapBadUpdateRow("Bad type", tbname, upd.key, upd.fieldname, k)

                if commit:
                    self.store.setdefault(tbname, {}).setdefault(upd.key, {})[upd.fieldname] = v

    def remove(self, remove_data):
        success = False
        for commit in [ False, True ]:
            upd = remove_data
            if upd:

                k, v = ProtoHelpers.decodeAttributeValueToTypeValue(upd.value)

                if upd.fieldname not in self.fields:
                    raise DapBadUpdateRow("No such field", None, upd.key, upd.fieldname, k)
                else:
                    tbname = self.fields[upd.fieldname]["tablename"]
                    ftype = self.fields[upd.fieldname]["type"]

                if ftype != k:
                    raise DapBadUpdateRow("Bad type", tbname, upd.key, upd.fieldname, k)

                if commit:
                    success |= self.store[tbname][upd.key].pop(upd.fieldname, None) is not None
        return success

    def removeAll(self, key):
        success = False
        for tbname in self.store:
            success |= self.store[tbname].pop(key, None) is not None
        return success
