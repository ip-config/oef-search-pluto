from typing import Callable

from dap_api.src.protos import dap_description_pb2

from dap_api.src.python import DapInterface
from dap_api.src.python import SubQueryInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python.DapInterface import DapBadUpdateRow

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

        for table_name, fields in self.structure_pb.items():
            self.tablenames.append(table_name)
            for field_name, field_type in fields.items():
                self.structure.setdefault(table_name, {}).setdefault(field_name, {})['type'] = field_type

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

    """This function queries one or more tables in this DAP, applying filtering and returns
    a list of all matching Agents which are in the pre-filtered list.

    Args:
      query (DapQuery): A query subtree which can be handled by this DAP.
      agents (DapResult): A sub-result which can be used to optimise or post-filter the results or NONE.

    Returns:
      DapResult
    """
    #def query(self, dapQuery, agents=None):
    #    for table_name, table in self.store.items():
    #        if agents:
    #            for key in agents:
    #                row=table[key]
    #                if dapQuery.testRow(row):
    #                    yield key
    #        for key, row in table.items():
    #            if dapQuery.testRow(row):
    #                yield key

    def processRows(self, rowProcessor, agents=None):
        for table_name, table in self.store.items():
            if agents == None:
                for key, row in table.items():
                    if rowProcessor(row):
                        yield key
            else:
                for key in agents:
                    row=table[key]
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

  #  def makeQuery(self, query_pb, constraint_factory, tablename):
  #      # This PB will be all the same table and all answerable by this object.
  #      dapQuery = DapQuery.DapQuery()
  #      dapQuery.fromQueryProto(query_pb, constraint_factory, self.structure.get(tablename, {}))
  #      return dapQuery

    def _typeOfDapValue(self, dap_value):
        return {
            2: "string",
            3: "int64",
            4: "float",
            5: "double",
            6: "embedding",
        }.get(dap_value.type, None)

    def print(self):
        print(self.store)

    # given an input value probuf, returnm the type and TRANSLATED TO PYTHON data in a tuple.
    def _typeAndValueOfDapValue(self, dap_value):
        (k, va) = {
            2: ("string", lambda x: x.s),
            3: ("int64", lambda x: x.i),
            4: ("float", lambda x: x.f),
            5: ("double", lambda x: x.d),
            6: ("embedding", lambda x: x.embedding.v),
        }.get(dap_value.type, (None, lambda x: None))
        return k, va(dap_value)

    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    def update(self, update_data):
        for commit in [ False, True ]:
            for upd in update_data.update:

                k,v = self._typeAndValueOfDapValue(upd.value)

                if upd.tablename not in self.structure:
                    raise DapBadUpdateRow("No such table", upd.tablename, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)

                if upd.fieldname not in self.structure[upd.tablename]:
                    raise DapBadUpdateRow("No such field", upd.tablename, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)

                if self.structure[upd.tablename][upd.fieldname]['type'] != k:
                    raise DapBadUpdateRow("Bad type", upd.tablename, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)

                if commit:
                    for core_uri in  upd.key.core_uri:
                        self.store.setdefault(upd.tablename, {}).setdefault(
                            (upd.key.agent_name, core_uri), {}
                        )[upd.fieldname] = v
