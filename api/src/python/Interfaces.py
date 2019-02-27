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


class HasResponseBuilder(ABC):
    @abstractmethod
    def build_responses(self, proto_list):
        pass


class HasResponseMerger(ABC):
    @abstractmethod
    def get_response_type(self):
        pass

    @abstractmethod
    def merge_response(self, resps):
        pass
