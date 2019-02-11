from typing import Callable

from dap_api.src.protos import dap_description_pb2

from dap_api.src.python import DapInterface
from dap_api.src.python import SubQueryInterface
from dap_api.src.python import DapOperatorFactory
from dap_api.src.python import DapQueryRepn
from dap_api.src.python import ProtoHelpers
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.protos import dap_update_pb2

from dap_e_r_network.src.python import Graph

class DapERNetwork(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, configuration):
        self.name = name
        self.graphs = {}
        self.structure_pb = configuration['structure']

        for table_name, fields in self.structure_pb.items():
            self.graphs[table_name] = Graph.Graph()

        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()

    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        for table_name in self.graphs.keys():
            result_table = result.table.add()
            result_table.name = table_name

            result_field = result_table.field.add()
            result_field.name = table_name + ".origin"
            result_field.type = "string"

            result_field = result_table.field.add()
            result_field.name = table_name + ".weight"
            result_field.type = "double"

        return result

    def getGraphByTableName(self, table_name):
        return self.graphs[table_name]

    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        raise Exception("TODO")

    def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
        raise Exception("DapERNetwork must create queries from subtrees, not leaves")

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

                # we're 

                k, v = ProtoHelpers.decodeAttributeValueToTypeValue(upd.value)

                if upd.fieldname not in self.fields:
                    raise DapBadUpdateRow("No such field", None, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)
                else:
                    tbname = self.fields[upd.fieldname]["tablename"]
                    ftype = self.fields[upd.fieldname]["type"]

                if ftype != k:
                    raise DapBadUpdateRow("Bad type", tbname, upd.key.agent_name, upd.key.core_uri, upd.fieldname, k)

                if commit:
                    for core_uri in  upd.key.core_uri:
                        self.store.setdefault(tbname, {}).setdefault(
                            (upd.key.agent_name, core_uri), {}
                        )[upd.fieldname] = v
