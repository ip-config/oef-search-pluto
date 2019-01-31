from dap_api.src.protos import dap_description_pb2

from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.python import DapQuery
from dap_api.src.python.DapConstraintFactory import DapConstraintFactory
from dap_api.src.python.DapConstraintFactory import g_dapConstraintFactory

class InMemoryDap(object):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, configuration):
        self.store = {}
        self.name = name
        self.structure_pb = configuration['structure']
        self.constraint_factory = g_dapConstraintFactory

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
    def query(self, dapQuery, agents=None):
        for table_name, table in self.store.items():
            for key, row in table.items():
                if dapQuery.testRow(row):
                    yield key

    def makeQuery(self, query_pb, tablename):
        dapQuery = DapQuery.DapQuery()
        dapQuery.fromQueryProto(query_pb, self.constraint_factory, self.structure.get(tablename, {}))
        return dapQuery

    def _typeOfDapValue(self, dap_value):
        return {
            2: "string",
            3: "int32",
            4: "float",
        }.get(dap_value.type, None)

    def _typeAndValueOfDapValue(self, dap_value):
        (k, va) = {
            2: ("string", lambda x: x.s),
            3: ("int32", lambda x: x.i),
            4: ("float", lambda x: x.f),
        }.get(dap_value.type, (None, lambda x: None))
        return (k, va(dap_value))

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
