from api.src.proto import response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from ai_search_engine.src.python.SearchEngine import SearchEngine
from api.src.python.ProtoWrappers import ProtoWrapper
from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python.DapManager import DapManager
from dap_api.experimental.python.AddressRegistry import AddressRegistry


class SearchQuery(HasProtoSerializer, HasMessageHandler):

    @has_logger
    def __init__(self, dap_manager: DapManager, proto_wrapper: ProtoWrapper, address_registry: AddressRegistry):
        self._dap_manager = dap_manager
        self._proto_wrapper = proto_wrapper
        self._address_registry = address_registry

    @serializer
    def serialize(self, data: bytes) -> query_pb2.Query.Model:
        pass

    @deserializer
    def deserialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass

    async def handle_message(self, msg: query_pb2.Query.Model) -> response_pb2.SearchResponse:
        resp = response_pb2.SearchResponse()
        query = self._proto_wrapper.get_instance(msg)
        result = self._dap_manager.execute(query.toDapQuery())
        items = []
        for element in result:
            item = response_pb2.SearchResponse.Item()
            addresses = self._address_registry.resolve(element())
            if len(addresses) > 0:
                address = addresses[0]
                item.ip = address.ip
                item.port = address.port
                item.key = element()
                #item.info = data model names registered with this oef
            else:
                self.log.warn("Ignoring result because no address found!")
                print("Query: ", msg)
                print("Result: ", element)
                continue
            item.score = element.score
            items.append(item)
        resp.result.extend(items)
        return resp
