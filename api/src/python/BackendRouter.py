from api.src.python.Serialization import JsonResponse
from api.src.python.Interfaces import HasProtoSerializer, HasMessageHandler
from utils.src.python.Logging import has_logger


class BackendRouter:
    @has_logger
    def __init__(self):
        self.__routing_serializer = {}
        self.__routing_handler = {}

    def register_serializer(self, path: str, obj: HasProtoSerializer):
        self.__routing_serializer[path] = obj

    def register_handler(self, path: str, obj: HasMessageHandler):
        self.__routing_handler[path] = obj

    async def route(self, path: str, data) ->bytes:
        if path in self.__routing_serializer:
            serializer = self.__routing_serializer[path]
            msg = await serializer.serialize(data)
            if path in self.__routing_handler:
                response = await self.__routing_handler[path].handle_message(msg)
                if isinstance(data, dict):
                    response = JsonResponse(response)
                return await serializer.deserialize(response)
            else:
                self.log.error("Message handler not register for path: ", path)
                return []
        else:
            self.log.error("Serializer not registered for path: ", path)
            return []
