from api.src.python.Serialization import Serializable
from api.src.python.Interfaces import HasProtoSerializer, HasMessageHandler, HasResponseBuilder, HasResponseMerger, DataWrapper
from utils.src.python.Logging import has_logger
import asyncio


class BackendRouter:
    @has_logger
    def __init__(self, name: str = ""):
        self.__routing_serializer = {}
        self.__routing_handler = {}
        self.__response_builder = {}
        self.__response_merger = {}
        self.name = name

    def register_serializer(self, path: str, obj: HasProtoSerializer):
        self.__routing_serializer[path] = obj

    def register_handler(self, path: str, obj: HasMessageHandler):
        self.__routing_handler.setdefault(path, set()).add(obj)

    def register_response_builder(self, path: str, obj: HasResponseBuilder):
        self.__response_builder[path] = obj

    def register_response_merger(self, obj: HasResponseMerger):
        self.__response_merger[obj.get_response_type()] = obj

    def __flatten_list(self, src):
        if type(src) != list:
            return [src]
        result = []
        for e in src:
            flatten = self.__flatten_list(e)
            result.extend(flatten)
        return result

    async def route(self, path: str, data) -> DataWrapper[bytes]:
        if path in self.__routing_serializer:
            serializer = self.__routing_serializer[path]
            msg = await serializer.deserialize(data)
            if path in self.__routing_handler:
                cos = []
                for handler in self.__routing_handler[path]:
                    cos.append(asyncio.create_task(handler.handle_message(msg)))
                response_list = await asyncio.gather(*cos, return_exceptions=True)
                if len(response_list) == 1:
                    response = response_list[0]
                else:
                    protos_by_type = {}
                    for p in response_list:
                        if p is None:
                            continue
                        if isinstance(p, Exception):
                            self.log.exception("Exception happened in handler for path {}: {}".format(path, str(p)))
                            continue
                        elif isinstance(p, list):
                            if len(p) == 0:
                                continue
                            d = self.__flatten_list(p)
                        else:
                            d = [p]
                        for e in d:
                            if not e.success or e.data is None:
                                self.info("Error in handlers: code: ", e.error_code, ", message: ", e.msg(), ", data: ",
                                          e.data)
                                continue
                            protos_by_type.setdefault(e.data.__class__, []).append(e)
                    merged_list = []
                    for k in protos_by_type:
                        if len(protos_by_type[k]) == 0:
                            continue
                        if k in self.__response_merger:
                            merged_list.append(self.__response_merger[k].merge_response(protos_by_type[k]))
                        else:
                            for e in protos_by_type[k]:
                                merged_list.append(e)
                    if len(merged_list) == 1:
                        response = merged_list[0]
                    elif len(merged_list) == 0:
                        self.log.warning("Empty merged list")
                        return DataWrapper(False, path, b'', 61, "Merged list is empty")
                    else:
                        self.info("Using response builder for path ", path, " for list: ", [p.data for p in merged_list])
                        response = self.__response_builder[path].build_responses(merged_list)
                if not response.success:
                    self.warning("Error in route handler for path %s, error_code %d, message: %s", path,
                                 response.error_code, response.msg())

                wrapped_data = Serializable(response.data)
                if isinstance(data, dict):
                    wrapped_data.target_type = Serializable.TargetType.JSON
                serialized_response = await serializer.serialize(wrapped_data)
                return DataWrapper(response.success, path, serialized_response, response.error_code, "",
                                   response.narrative, id=response.id)
            else:
                msg = "Message handler not register for path: %s" % path
                self.log.error(msg)
                return DataWrapper(False, path, b'', 53, msg)
        else:
            msg = "Serializer not registered for path: %s" % path
            self.log.error(msg)
            return DataWrapper(False, path, b'', 53, msg)
