from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from api.src.proto.core import update_pb2
from api.src.proto.core import response_pb2
from dap_api.src.python.DapManager import DapManager
from api.src.python.core.ProtoWrappers import ProtoWrapper, InvalidAttribute, MissingAddress

ResponseType = response_pb2.UpdateResponse.ResponseType


def process_update(self, msg) -> DataWrapper[response_pb2.UpdateResponse]:
    resp = response_pb2.UpdateResponse()
    try:
        upd = self.proto_wrapper.get_instance(msg)
        self.dap_manager.update(upd.toDapUpdate())
        resp.status = ResponseType.Value("SUCCESS")
    except InvalidAttribute as e:
        msg = "Got invalid attribute: " + str(e)
        resp.status = ResponseType.Value("INVALID_ATTRIBUTE")
        resp.message = msg
        self.log.info(msg)
    except MissingAddress as e:
        resp.status = ResponseType.Value("MISSING_ADDRESS")
        msg = str(e)
        resp.message = msg
        self.log.info(msg)
    except Exception as e:
        msg = "Failed to update data, because: " + str(e)
        resp.status = ResponseType.Value("ERROR")
        resp.message = msg
        self.warning(msg)
    return DataWrapper(True, "update", resp)


class UpdateEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self, dap_manager: DapManager, proto_wrapper: ProtoWrapper):
        self.dap_manager = dap_manager
        self.proto_wrapper = proto_wrapper

    @deserializer
    def deserialize(self, data: bytes) -> update_pb2.Update:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.UpdateResponse) -> bytes:
        pass

    async def handle_message(self, msg: update_pb2.Update) -> DataWrapper[response_pb2.UpdateResponse]:
        return process_update(self, msg)


class BlkUpdateEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self, dap_manager: DapManager, proto_wrapper: ProtoWrapper):
        self.dap_manager = dap_manager
        self.proto_wrapper = proto_wrapper

    @deserializer
    def deserialize(self, data: bytes) -> update_pb2.Update.BulkUpdate:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.UpdateResponse) -> bytes:
        pass

    async def handle_message(self, msg: update_pb2.Update.BulkUpdate) -> \
            DataWrapper[response_pb2.UpdateResponse]:
        return process_update(self, msg)
