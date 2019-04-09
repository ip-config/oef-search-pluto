from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from api.src.proto.director import core_pb2
from utils.src.python.Logging import has_logger
from dap_api.src.python.DapManager import DapManager
from dap_api.src.protos import dap_update_pb2


class LocationEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self,  dap_manager: DapManager, db_structure: dict):
        self._dap_manager = dap_manager
        self._db_structure = db_structure
        pass

    @deserializer
    def deserialize(self, data: bytes) -> core_pb2.CoreLocation:
        pass

    @serializer
    def serialize(self, proto_msg: core_pb2.Response) -> bytes:
        pass

    async def handle_message(self, msg: core_pb2.CoreLocation) -> DataWrapper[core_pb2.Response]:
        response = DataWrapper(False, "location", core_pb2.Response())
        update = dap_update_pb2.DapUpdate()
        try:
            upd = update.update.add()
            upd.tablename = self._db_structure["table"]
            upd.fieldname = self._db_structure["field"]
            upd.key.core = msg.core_key
            upd.value.type = 9
            upd.value.l.CopyFrom(msg.location)
        except Exception as e:
            msg = "Failed to create dap_update proto from director location update: ", str(e)
            self.warning(msg)
            response.error_code = 500
            response.add_narrative(msg)

        try:
            status = self._dap_manager.update(update)
            response.success = status
        except Exception as e:
            msg = "DapManager: failed update: " + str(e)
            response.add_narrative(msg)
            self.warning(msg)

        return response
