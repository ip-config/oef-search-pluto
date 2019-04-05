from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from api.src.proto.director import core_pb2
from utils.src.python.Logging import has_logger


class LocationEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self):
        pass

    @deserializer
    def deserialize(self, data: bytes) -> core_pb2.CoreLocation:
        pass

    @serializer
    def serialize(self, proto_msg: core_pb2.Response) -> bytes:
        pass

    async def handle_message(self, msg: core_pb2.CoreLocation) -> DataWrapper[core_pb2.Response]:
        return DataWrapper(False, "", b'')
