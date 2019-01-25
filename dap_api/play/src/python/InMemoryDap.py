
from dap_api.src.protos import dap_description_pb2

class InMemoryDap(object):

    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, structure):
        self.store = {}
        self.name = name
        self.structure = structure

    """This function returns the DAP description which lists the
    tables it hosts, the fields within those tables and the result of
    a lookup on any of those tables.

    Returns:
       DapDescription
    """
    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        for table_name, fields in self.structure.items():
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
    def query(self, query, agents=None):
        pass


    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    def update(self, update_data):
        for upd in update_data.update:
            k = (upd.tablename, upd.key.agent_name, upd.key.core_uri, fieldname)

            v = upd.value.i
            if upd.HasField('f'):
                v = upd.value.f
            if upd.HasField('s'):
                v = upd.value.s

            store[k] = v
