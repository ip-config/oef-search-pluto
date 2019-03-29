from api.src.proto import response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, HasResponseMerger
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from api.src.python.ProtoWrappers import ProtoWrapper
from api.src.proto import query_pb2
from dap_api.src.python.DapManager import DapManager
from dap_in_memory.src.python.AddressRegistry import AddressRegistry
from typing import List


class SearchQuery(HasProtoSerializer, HasMessageHandler, HasResponseMerger):

    @has_logger
    def __init__(self, dap_manager: DapManager, proto_wrapper: ProtoWrapper, address_registry: AddressRegistry):
        self._dap_manager = dap_manager
        self._proto_wrapper = proto_wrapper
        self._address_registry = address_registry

    @deserializer
    def deserialize(self, data: bytes) -> query_pb2.Query:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass

    def get_response_type(self):
        return response_pb2.SearchResponse().__class__

    def merge_response(self, resps: List[response_pb2.SearchResponse]) -> response_pb2.SearchResponse:
        resp = response_pb2.SearchResponse()
        keys = []
        for r in resps:
            result = []
            for rr in r.result:
                if rr.key in keys:
                    continue
                keys.append(rr.key)
                result.append(rr)
            resp.result.extend(result)
        return resp

    async def handle_message(self, msg: query_pb2.Query) -> response_pb2.SearchResponse:
        resp = response_pb2.SearchResponse()
        query = self._proto_wrapper.get_instance(msg.model)
        result = self._dap_manager.execute(query.toDapQuery())
        items = {}
        for element in result.identifiers:
            core, agent_id = element.core, element.agent
            if core not in items:
                item = response_pb2.SearchResponse.Item()
                addresses = self._address_registry.resolve(core)
                if len(addresses) > 0:
                    address = addresses[0]
                    item.ip = address.ip
                    item.port = address.port
                    item.key = core
                #item.info = data model names registered with this oef
                else:
                    self.log.warning("Ignoring result because no address found!")
                    print("Query: ", msg)
                    print("Result: ", element)
                    continue
                item.score = element.score
                items[core] = item
            agent = items[core].agents.add()
            agent.key = agent_id
        resp.result.extend(items.values())
        return resp
