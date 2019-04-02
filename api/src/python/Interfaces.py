from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, List


class HasProtoSerializer(ABC):
    @abstractmethod
    def serialize(self, data):
        pass

    @abstractmethod
    def deserialize(self, proto_msg):
        pass


T = TypeVar('T')


class DataWrapper(Generic[T]):
    def __init__(self, success: bool, uri: str, data: T, error_code: int = 0, narrative: str = "",
                 narrative_list: List[str] = list()):
        self.uri = uri
        self.success = success
        self.data = data
        self.error_code = error_code
        self.narrative = []
        if len(narrative) > 0:
            self.add_narrative(narrative)
        if len(narrative_list) > 0:
            for n in narrative_list:
                self.add_narrative(n)

    def add_narrative(self, narrative: str):
        self.narrative.append(narrative)

    def msg(self):
        return " ".join(self.narrative)


class HasMessageHandler(ABC):
    @abstractmethod
    def handle_message(self, msg) -> DataWrapper[Any]:
        pass


class HasResponseBuilder(ABC):
    @abstractmethod
    def build_responses(self, response_list: DataWrapper[Any]) -> DataWrapper[Any]:
        pass


class HasResponseMerger(ABC):
    @abstractmethod
    def get_response_type(self):
        pass

    @abstractmethod
    def merge_response(self, resps: DataWrapper[Any]) -> DataWrapper[Any]:
        pass
