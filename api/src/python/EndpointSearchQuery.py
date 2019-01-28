from api.src.proto import query_pb2, response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer


class SearchQuery(HasProtoSerializer, HasMessageHandler):

    @serializer
    def serialize(self, data: bytes) -> query_pb2.Query:
        pass

    @deserializer
    def deserialize(self, proto_msg: response_pb2.Response) -> bytes:
        pass

    async def handle_message(self, msg: query_pb2.Query) -> response_pb2.Response:
        resp = response_pb2.Response()
        resp.name = "Hello " + msg.name + ", I'm Server"
        return resp
