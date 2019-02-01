from api.src.proto import response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from ai_search_engine.src.python.SearchEngine import SearchEngine
from api.src.python.ProtoWrappers import ProtoWrapper
from fetch_teams.oef_core_protocol import query_pb2


class SearchQuery(HasProtoSerializer, HasMessageHandler):

    @has_logger
    def __init__(self, search_engine: SearchEngine, proto_wrapper: ProtoWrapper):
        self._search_engine = search_engine
        self._proto_wrapper = proto_wrapper

    @serializer
    def serialize(self, data: bytes) -> query_pb2.Query.Model:
        pass

    @deserializer
    def deserialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass

    async def handle_message(self, msg: query_pb2.Query.Model) -> response_pb2.SearchResponse:
        resp = response_pb2.SearchResponse()
        proto = self._proto_wrapper.get_instance(msg)
        result = self._search_engine.query(proto.toDapQuery())
        items = []
        for element in result:
            item = response_pb2.SearchResponse.Item()
            item.agent = element[0][1]
            if type(element[0][1]) == list:
                item.oef_core.extend(element[0][0])
            else:
                item.oef_core.extend([element[0][0]])
            item.score = element[1]
            items.append(item)
        resp.result.extend(items)
        return resp