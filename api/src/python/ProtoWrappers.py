from api.src.proto import update_pb2
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python.DapQuery import DapQuery
from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger
from dap_api.src.python.DapManager import DapManager


class ProtoWrapper:
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def get_instance(self, data):
        return self.cls(data, *self.args, **self.kwargs)


class UpdateData:

    def __init__(self, origin: update_pb2.Update, db_structure):
        self.origin = origin
        self.db_structure = db_structure

    def _set_uri(self, upd: dap_update_pb2.DapUpdate.TableFieldValue, origin: update_pb2.Update):
        agent, oef_core = origin.uri.agent, origin.uri.oef_core
        upd.key.agent_name = agent
        upd.key.core_uri.extend(oef_core)

    def _set_tb_field(self, upd: dap_update_pb2.DapUpdate.TableFieldValue):
        upd.tablename = self.db_structure["table"]
        upd.fieldname = self.db_structure["field"]

    def _set_value(self, upd: dap_update_pb2.DapUpdate.DapValue, origin: update_pb2.Update):
        upd.type = 6
        upd.dm.name = origin.data_model.name
        upd.dm.description = origin.data_model.description
        upd.dm.attributes.extend(origin.data_model.attributes)

    def toDapUpdate(self) -> update_pb2.Update:
        updates = []
        try:
            updates = self.origin.list
        except:
            updates = [self.origin]
        upd_list = []
        for origin in updates:
            upd = dap_update_pb2.DapUpdate.TableFieldValue()
            self._set_tb_field(upd)
            self._set_uri(upd, origin)
            self._set_value(upd.value, origin)
            upd_list.append(upd)
        upd = dap_update_pb2.DapUpdate()
        upd.update.extend(upd_list)
        return upd


class QueryData:

    @has_logger
    def __init__(self, origin: query_pb2.Query.Model, dap_manager: DapManager):
        self.origin = origin
        self.dap_manager = dap_manager
        if not self.origin:
            self.origin = query_pb2.Query()

    # TODO support for constraints
    def toDapQuery(self):
        return self.dap_manager.makeQuery(self.origin)
