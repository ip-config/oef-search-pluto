from api.src.proto.core import response_pb2
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, HasResponseMerger, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from utils.src.python.distance import geo_distance
from api.src.python.core.ProtoWrappers import ProtoWrapper
from api.src.proto.core import query_pb2
from dap_api.src.python.DapManager import DapManager
from typing import List


class SearchEndpoint(HasProtoSerializer, HasMessageHandler, HasResponseMerger):

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
        distance = None
        try:
            location = self._dap_manager.getPlaneInformation("location")["values"]
            if len(location) > 1:
                self.warning("Got more then 1 location from dapManager (I'm using first, ignoring the rest now): ",
                             location)
            #TODO: multiple core
            location = location[0].value.l
            prev_distance = msg.directed_search.distance.geo
            target = msg.directed_search.target.geo
            distance = geo_distance(location, target)
            if prev_distance > 0 and distance > prev_distance:
                #ignore query
                self.warning("Ignoring query with TTL %d, because source (%s) distance (%.3f) was smaller then "
                             "my distance (%.3f)", msg.ttl, msg.source_key.decode("UTF-8"), prev_distance, distance)
                return DataWrapper(False, "search", resp, 601, "Ignoring query because distance!")
            else:
                self.info("Handling query with TTL %d, because source (%s) distance (%.3f) was greater then"
                          " my distance (%.3f)", msg.ttl, msg.source_key.decode("UTF-8"), prev_distance, distance)
        except Exception as e:
            #TODO: what?
            self.exception("Exception during location check: ", str(e))
            #return DataWrapper(False, "search", resp, 600, "Ignoring query, location check error!")
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
                    if distance:
                        #TODO multiple core
                        item.distance = distance
                agent = items[core].agents.add()
                agent.key = agent_id
            resp.result.extend(items.values())
        except Exception as e:
            self.exception("Exception while processing query: ", str(e))
            return DataWrapper(False, "search", resp, 500, str(e))
        return DataWrapper(True, "search", resp)
