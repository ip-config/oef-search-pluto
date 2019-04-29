import abc
from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer, DataWrapper
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from api.src.proto.director import node_pb2
from api.src.proto.director import core_pb2


class ConnectionManager(abc.ABC):
    @abc.abstractmethod
    def add_peer(self, name: str, host: str, port: int) -> bool:
        pass


class PeerEndpoint(HasProtoSerializer, HasMessageHandler):
    @has_logger
    def __init__(self,  connection_manager: ConnectionManager):
        self._manager = connection_manager
        pass

    @deserializer
    def deserialize(self, data: bytes) -> node_pb2.PeerUpdate:
        pass

    @serializer
    def serialize(self, proto_msg: core_pb2.Response) -> bytes:
        pass

    async def handle_message(self, msg: node_pb2.PeerUpdate) -> DataWrapper[core_pb2.Response]:
        response = DataWrapper(True, "peer", core_pb2.Response())
        try:
            self.info("ADD PEERS: ", msg)
            for peer in msg.add_peers:
                self._manager.add_peer(peer.name, peer.host, peer.port)
        except Exception as e:
            self.exception(e)
            response.success = False
        return response
