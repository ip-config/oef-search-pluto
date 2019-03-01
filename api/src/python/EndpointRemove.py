from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from api.src.proto import remove_pb2, update_pb2
from api.src.proto import response_pb2
from dap_api.src.python.DapManager import DapManager
from api.src.python.ProtoWrappers import ProtoWrapper, InvalidAttribute, MissingAddress

ResponseType = response_pb2.RemoveResponse.ResponseType


def toUpdate(msg: remove_pb2.Remove) -> update_pb2.Update:
    upd = update_pb2.Update()
    upd.key = msg.key
    upd.attributes.extend(msg.attributes)
    upd.data_models.extend(msg.data_models)
    return upd


class RemoveEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self, dap_manager: DapManager, proto_wrapper: ProtoWrapper):
        self.dap_manager = dap_manager
        self.proto_wrapper = proto_wrapper

    @deserializer
    def deserialize(self, data: bytes) -> remove_pb2.Remove:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.RemoveResponse) -> bytes:
        pass

    async def handle_message(self, msg: remove_pb2.Remove) -> response_pb2.UpdateResponse:
        resp = response_pb2.RemoveResponse()
        try:
            if msg.all:
                status = self.dap_manager.removeAll(msg.key)
            else:
                upd = self.proto_wrapper.get_instance(toUpdate(msg))
                status = self.dap_manager.remove(upd.toDapUpdate())
            if status:
                resp.status = ResponseType.Value("SUCCESS")
            else:
                resp.status = ResponseType.Value("NOT_FOUND")
        except Exception as e:
            resp.status = ResponseType.Value("ERROR")
            resp.message = str(e)
        return resp
