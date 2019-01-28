from abc import ABC, abstractmethod


class HasProtoSerializer(ABC):
    @abstractmethod
    def serialize(self, data):
        pass

    @abstractmethod
    def deserialize(self, proto_msg):
        pass


class HasMessageHandler(ABC):
    @abstractmethod
    def handle_message(self, msg):
        pass
