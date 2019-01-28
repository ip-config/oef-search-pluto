from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from oef_core.oef_core_protocol import query_pb2
from api.src.proto import response_pb2


class SearchEngine:
    @has_logger
    def __init__(self):
        self._storage = {}

    def add(self, key, data):
        self.log.info("Got key %s and data %s" % (key, data))
        self._storage[key] = data


class UpdateEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self, search_engine: SearchEngine):
        self.search_engine = search_engine

    @serializer
    def serialize(self, data: bytes) -> query_pb2.Query.Instance:
        pass

    @deserializer
    def deserialize(self, proto_msg: response_pb2.UpdateResponse) -> bytes:
        pass

    async def handle_message(self, msg: query_pb2.Query) -> response_pb2.Response:
        self.log.info("Got message: "+msg.SerializeToString())
        resp = response_pb2.Response()
        return resp
