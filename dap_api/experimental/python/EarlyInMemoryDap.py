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
from utils.src.python.Logging import has_logger


class EarlyInMemoryDap(DapInterface.DapInterface):
    @has_logger

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    def __init__(self, name, configuration):
        self.store = {}
        self.name = name
        self.structure_pb = configuration['structure']
        self.log.update_local_name("EarlyInMemoryDap("+name+")")
        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()

        self.tablenames = []
        self.structure = {}
        self.fields = {}

        self.all_my_keys = set()

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

        result.options.append("early")

        star_table = result.table.add()
        star_table.name = '*'

        star_field = star_table.field.add()
        star_field.name = '*'
        star_field.type = '*'

        return result

    # returns an object with an execute(agents=None) -> [agent]
    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        return None

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        result = dap_interface_pb2.IdentifierSequence()
        cores = proto.input_idents
        query_memento = proto.query_memento
        j = json.loads(query_memento.memento.decode("utf-8"))

        if cores.originator:
            for row_key in self.all_my_keys:
                core_ident, agent_ident = row_key
                self.log.info("RETURNING ORIGINATED: core={}, agent={}".format(core_ident, agent_ident))
                i = result.identifiers.add()
                i.core = core_ident
                i.agent = agent_ident
        else:
            for key in cores.identifiers:
                core_ident, agent_ident = key.core, key.agent
                self.log.info("RETURNING SUPPLIED: core={}, agent={}".format(core_ident, agent_ident))
                i = result.identifiers.add()
                i.core = core_ident
                i.agent = agent_ident


    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        j = {}
        j['target_field_name'] = '*'
        j['target_field_type'] = '*'

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

        upd = update_data
        if upd:
            row_key = (upd.key.core, upd.key.agent)
            core_ident, agent_ident = row_key
            self.all_my_keys.add(row_key)
            self.log.info("INSERT: core={}, agent={}".format(core_ident, agent_ident))

        return r

    def remove(self, remove_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:

        r = dap_interface_pb2.Successfulness()
        r.success = True

        success = False
        for commit in [ False, True ]:
            upd = remove_data
            row_key = (upd.key.core, upd.key.agent)
            self.all_my_keys.pop(row_key)
            self.log.info("REMOVE: core={}, agent={}".format(core_ident, agent_ident))
        return r
