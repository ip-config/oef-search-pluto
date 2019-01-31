from api.src.proto import query_pb2, response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from ai_search_engine.src.python.SearchEngine import SearchEngine
from api.src.python.ProtoWrappers import ProtoWrapper


class SearchQuery(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self, search_engine: SearchEngine, proto_wrapper: ProtoWrapper):
        self._search_engine = search_engine
        self._proto_wrapper = proto_wrapper

    @serializer
    def serialize(self, data: bytes) -> query_pb2.Query:
        pass

    @deserializer
    def deserialize(self, proto_msg: response_pb2.Response) -> bytes:
        pass

    async def handle_message(self, msg: query_pb2.Query) -> response_pb2.Response:
        resp = response_pb2.Response()
        resp.name = self._search_engine.search(self._proto_wrapper.get_instance(msg))
        return resp
