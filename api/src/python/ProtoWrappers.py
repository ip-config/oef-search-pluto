from api.src.proto import update_pb2
from dap_api.src.protos import dap_update_pb2
from dap_api.src.python.DapQuery import DapQuery
from fetch_teams.oef_core_protocol import query_pb2


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

    def _set_uri(self, upd: dap_update_pb2.DapUpdate):
        agent, oef_core = self.origin.uri.agent, self.origin.uri.oef_core
        upd.key.agent_name = agent
        upd.key.core_uri.extemd(oef_core)

    def _set_tb_field(self, upd: dap_update_pb2.DapUpdate):
        upd.tablename = self.db_structure["table"]
        upd.fieldname = self.db_structure["field"]

    def _set_value(self, upd: dap_update_pb2.DapUpdate.DapValue):
        upd.type = 6
        upd.dm.name = self.origin.data_model.name
        upd.dm.description = self.origin.data_model.description
        upd.dm.attributes.extend(self.origin.data_model.attributes)

    def toDapUpdate(self) -> update_pb2.Update:
        upd = dap_update_pb2.DapUpdate()
        self.set_tb_field(upd)
        self.set_uri(upd)
        self.et_value(upd.value)
        return upd


class QueryData:

    def __init__(self, origin: query_pb2.Query):
        self.origin = origin
        if not self.origin:
            self.origin = query_pb2.Query()

    def add_description(self, text):
        self.origin.description = text

    def add_data_model(self, dm):
        self.origin.data_model = dm

    def toDapQuery(self):
        q = DapQuery()
        q.fromQueryProto(self.origin)
        return q