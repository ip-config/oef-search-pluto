import functools
from inspect import signature
from google.protobuf import json_format
import json


class JsonResponse:
    def __init__(self, data):
        self.data = data


def deserializer(func):
    sig = signature(func)
    return_type = sig.return_annotation
    assert return_type != sig.empty, \
        "Serialization function must have a protocol buffer return type!"
    assert hasattr(return_type, "ParseFromString"), \
        "Serialization function seems not to have a valid protocol buffer return type!"

    @functools.wraps(func)
    async def wrapper(self, data):
        if isinstance(data, dict):
            try:
                return json_format.Parse(json.dumps(data), return_type())
            except Exception as e:
                print("Exception while trying to parse json to protocol buffer!", e)
        else:
            try:
                msg = return_type()
                msg.ParseFromString(data)
                return msg
            except Exception as e:
                print("Exception while trying to parse data to protocol buffer!", e)
    return wrapper


def serializer(func):
    sig = signature(func)
    parameter_type = list(sig.parameters.values())[1]
    assert parameter_type != sig.empty, \
        "Deserialization function must first argument (not counting self) of protocol buffer type!"
    parameter_type = parameter_type.annotation
    assert hasattr(parameter_type, "SerializeToString"), \
        "Deserialization function seems not to have a valid protocol buffer first argument type!"

    @functools.wraps(func)
    async def wrapper(self, msg):
        if isinstance(msg, JsonResponse):
            try:
                return json_format.MessageToJson(msg.data)
            except Exception as e:
                print("Exception while trying to serialize protocol buffer to json!", e)
        else:
            try:
                return msg.SerializeToString()
            except Exception as e:
                print("Exception while trying to serialize protocol buffer!", e)
    return wrapper
