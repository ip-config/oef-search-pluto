import abc
from abc import abstractmethod
from typing import Callable

from dap_api.src.python import DapQueryRepn
from dap_api.src.python import SubQueryInterface

class DapInterface(abc.ABC):
    def __init__():
        pass

    """This function returns the DAP description which lists the
    tables it hosts, the fields within those tables and the result of
    a lookup on any of those tables.

    Returns:
       DapDescription
    """
    @abstractmethod
    def describe(self):
        pass

    """This function will be called with any update to this DAP.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      None
    """
    @abstractmethod
    def update(self, update_data):
        pass

    """This function will be called when the core wants to remove data from search
    
    Args:
        update (DapUpdate): The data which needs to be removed
        
    Returns:
      None
    """
    def remove(self, remove_data):
        pass

    """This function will be called when the core wants to remove all of it's data from search

        Args:
            key (string): the core key

        Returns:
          None
        """

    def removeAll(self, key):
        pass

    """This function will be called with parts of the query's AST. If
    the interface can construct a unified query for the whole subtree
    it may do so.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      Either a suitable SubQueryInterface object, or None to let the DapManager handle things.
    """
    @abstractmethod
    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        return None

    """This function will be called with leaf nodes of the query's
    AST.  The result should be a SubQueryInterface for the constraint object
    object OR None if the constraint cannot be matched.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      Either a suitable QueryExecutionInterface object, or None to let the DapManager handle things.
    """
    @abstractmethod
    def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
        pass

class DapBadUpdateRow(Exception):
    def __init__(
            self,
            message,
            table_name="?TABLE",
            core_key="?COREKEY",
            field_name="?FIELD",
            field_type="?FIELDTYPE",
            value_type="?TYPE",
            value=None
        ):
        self.message = message
        self.table_name = table_name
        self.core_key = core_key
        self.field_name = field_name
        self.value_type = value_type
        self.field_type = field_type
        self.value = value
        super(DapBadUpdateRow, self).__init__(
            "{}: table({}), field({})/({}), value({})/({}), core({})".format(
                message,
                self.table_name,
                self.field_name,
                self.field_type,
                self.value,
                self.value_type,
                self.core_key,
            )
        )
