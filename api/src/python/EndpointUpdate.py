from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from api.src.proto import update_pb2
from api.src.proto import response_pb2
from ai_search_engine.src.python.SearchEngine import SearchEngine
from api.src.python.ProtoWrappers import ProtoWrapper




class UpdateEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self, search_engine: SearchEngine, proto_wrapper: ProtoWrapper):
        self.search_engine = search_engine
        self.proto_wrapper = proto_wrapper

    @serializer
    def serialize(self, data: bytes) -> update_pb2.Update:
        pass

    @deserializer
    def deserialize(self, proto_msg: response_pb2.UpdateResponse) -> bytes:
        pass

    async def handle_message(self, msg: update_pb.Update) -> response_pb2.Response:
        resp = response_pb2.UpdateResponse()
        try:
            self.search_engine.update(self.proto_wrapper.get_instance(msg))
            resp.status = response_pb2.UpdateResponse.ResponseType.SUCCESS
        except Exception as e:
            self.log.info("Failed to update data, because: "+e)
            resp.status = response_pb2.UpdateResponse.ResponseType.ERROR
        return resp
