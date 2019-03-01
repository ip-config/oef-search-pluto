from api.src.python.Serialization import JsonResponse
from api.src.python.Interfaces import HasProtoSerializer, HasMessageHandler, HasResponseBuilder, HasResponseMerger
from utils.src.python.Logging import has_logger
import asyncio


class BackendRouter:
    @has_logger
    def __init__(self):
        self.__routing_serializer = {}
        self.__routing_handler = {}
        self.__response_builder = {}
        self.__response_merger = {}

    def register_serializer(self, path: str, obj: HasProtoSerializer):
        self.__routing_serializer[path] = obj

    def register_handler(self, path: str, obj: HasMessageHandler):
        self.__routing_handler.setdefault(path, set()).add(obj)

    def register_response_builder(self, path: str, obj: HasResponseBuilder):
        self.__response_builder[path] = obj

    def register_response_merger(self, obj: HasResponseMerger):
        self.__response_merger[obj.get_response_type()] = obj

    async def route(self, path: str, data) ->bytes:
        if path in self.__routing_serializer:
            serializer = self.__routing_serializer[path]
            msg = await serializer.serialize(data)
            if path in self.__routing_handler:
                cos = []
                for handler in self.__routing_handler[path]:
                    cos.append(handler.handle_message(msg))
                proto_list = await asyncio.gather(*cos, return_exceptions=True)
                if len(proto_list) == 1:
                    response = proto_list[0]
                else:
                    protos_by_type = {}
                    for p in proto_list:
                        if isinstance(p, Exception):
                            self.log.warn("Exception happened in handler for path {}: {}".format(path, str(p)))
                        else:
                            protos_by_type.setdefault(p.__class__, []).append(p)
                    merged_list = []
                    for k in protos_by_type:
                        if k in self.__response_merger:
                            merged_list.append(self.__response_merger[k].merge_response(protos_by_type[k]))
                        else:
                            merged_list.append(protos_by_type[k])
                    if len(merged_list) == 1:
                        response = merged_list[0]
                    else:
                        response = self.__response_builder[path].build_responses(merged_list)
                if isinstance(data, dict):
                    response = JsonResponse(response)
                return await serializer.deserialize(response)
            else:
                self.log.error("Message handler not register for path: ", path)
                return []
        else:
            self.log.error("Serializer not registered for path: ", path)
            return []
