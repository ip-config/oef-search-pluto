from typing import Callable

from dap_api.src.protos import dap_description_pb2

from dap_api.src.python import DapInterface
from dap_api.src.python import SubQueryInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.protos import dap_update_pb2
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
                    row = table[key()]
                    if rowProcessor(row):
                        yield key

    # returns an object with an execute(agents=None) -> [agent]
    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        return None

    class ConstraintProcessor(SubQueryInterface.SubQueryInterface):
        def __init__(self, inMemoryDap, rowProcessor, target_field_name):
            self.inMemoryDap = inMemoryDap
            self.func = lambda row: rowProcessor(row.get(target_field_name, None))

        def execute(self, agents=None):
            yield from self.inMemoryDap.processRows(self.func, agents)

    def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
        rowProcessor = self.operatorFactory.createAttrMatcherProcessor(
                dapQueryRepnLeaf.target_field_type,
                dapQueryRepnLeaf.operator,
                dapQueryRepnLeaf.query_field_type,
                dapQueryRepnLeaf.query_field_value)
        return InMemoryDap.ConstraintProcessor(self, rowProcessor, dapQueryRepnLeaf.target_field_name)

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
                    raise DapBadUpdateRow("No such field", None, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)
                else:
                    tbname = self.fields[upd.fieldname]["tablename"]
                    ftype = self.fields[upd.fieldname]["type"]

                if ftype != k:
                    raise DapBadUpdateRow("Bad type", tbname, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)

                if commit:
                    self.store.setdefault(tbname, {}).setdefault(upd.key, {})[upd.fieldname] = v
