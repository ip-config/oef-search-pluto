
# We don't really need this, because it's DUCK TYPED, but this is the
# interface definition for reference.


class DapInterface(object):
    def __init__():
        pass

    """This function returns the DAP description which lists the
    tables it hosts, the fields within those tables and the result of
    a lookup on any of those tables.

    Returns:
       DapDescription
    """
    def describe(self):
        pass


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
        pass


class DapBadUpdateRow(Exception):
    def __init__(
            self,
            message,
            table_name="?TABLE",
            agent_name="?AGENT",
            core_uri="?URI",
            field_name="?FIELD",
            value_type="?TYPE",
            value=None
        ):
        self.message = message
        self.table_name = table_name
        self.agent_name = agent_name
        self.core_uri = core_uri
        self.field_name = field_name
        self.value_type = value_type
        self.value = value
        super(DapBadUpdateRow, self).__init__(
            "{}: table({}), field({}), value({})/({}), agent(), core({})".format(
                message,
                self.table_name,
                self.field_name,
                self.value,
                self.value_type,
                self.agent_name,
                self.core_uri
            )
        )
