from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from api.src.proto.core import response_pb2
import copy


class SearchResponseSerialization(HasProtoSerializer):
    @deserializer
    def deserialize(self, data: bytes) -> response_pb2.SearchResponse:
        pass

    @serializer
    def serialize(self, proto_msg: response_pb2.SearchResponse) -> bytes:
        pass


class BroadcastFromNode(HasMessageHandler):
    def __init__(self, path, node):
        self._node = node
        self._path = path
        self._serializer = SearchResponseSerialization()

    def __flatten_list(self, src):
        if type(src) != list:
            if src is None:
                return []
            return [src]
        result = []
        for e in src:
            flatten = self.__flatten_list(e)
            result.extend(flatten)
        return result

    async def handle_message(self, msg):
        response = await self._node.broadcast(self._path, copy.deepcopy(msg))
        if type(response) != list:
            response = [response]
        response = self.__flatten_list(response)
        transformed = []
        for r in response:
            if len(r.data) < 1:
                deserialized = None
            else:
                deserialized = await self._serializer.deserialize(r.data)
            transformed.append(DataWrapper(r.success, r.uri, deserialized, r.error_code, "", r.narrative, r.id))
        return transformed
