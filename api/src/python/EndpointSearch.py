from api.src.proto import response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, HasResponseMerger, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from api.src.python.ProtoWrappers import ProtoWrapper
from api.src.proto import query_pb2
from dap_api.src.python.DapManager import DapManager
from typing import List


class SearchQuery(HasProtoSerializer, HasMessageHandler, HasResponseMerger):

    @has_logger
    def __init__(self, dap_manager: DapManager, proto_wrapper: ProtoWrapper):
        self._dap_manager = dap_manager
        self._proto_wrapper = proto_wrapper

    @deserializer
    def deserialize(self, data: bytes) -> query_pb2.Query:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass

    def get_response_type(self):
        return response_pb2.SearchResponse().__class__

    def merge_response(self, resps: List[DataWrapper[response_pb2.SearchResponse]]) -> \
            DataWrapper[response_pb2.SearchResponse]:
        resp = response_pb2.SearchResponse()
        error_code = 1000
        narrative = []
        keys = []
        success = False
        for r in resps:
            result = []
            success |= r.success
            error_code = min(error_code, r.error_code)
            narrative.extend(r.narrative)
            for rr in r.data.result:
                if rr.key in keys:
                    continue
                keys.append(rr.key)
                result.append(rr)
            resp.result.extend(result)
        return DataWrapper(success, "search", resp, error_code, "", narrative)

    async def handle_message(self, msg: query_pb2.Query) -> DataWrapper[response_pb2.SearchResponse]:
        resp = response_pb2.SearchResponse()
        try:
            query = self._proto_wrapper.get_instance(msg.model)
            result = self._dap_manager.execute(query.toDapQuery())
            items = {}
            for element in result.identifiers:
                core, agent_id = element.core, element.agent
                if core not in items:
                    item = response_pb2.SearchResponse.Item()
                    address = element.uri.split(":")
                    if len(address) != 2:
                        self.warning("No valid address for core: ", core, "! address=", address)
                        continue
                    item.ip = address[0]
                    item.port = int(address[1])
                    item.key = core
                    item.score = element.score
                    items[core] = item
                agent = items[core].agents.add()
                agent.key = agent_id
            resp.result.extend(items.values())
        except Exception as e:
            self.exception("Exception while processing query: ", str(e))
            return DataWrapper(False, "search", resp, 500, str(e))
        return DataWrapper(True, "search", resp)
