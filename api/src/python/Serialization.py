import functools
from inspect import signature
from google.protobuf import json_format
import json
from utils.src.python.Logging import get_logger


def _process_tupple(data):
    if isinstance(data, tuple):
        if data[0] is None:
            return data[1]
        else:
            return data[0]
    else:
        return data


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
    log = get_logger("Deserializer")

    @functools.wraps(func)
    async def wrapper(self, data):
        nonlocal log
        if isinstance(data, dict):
            try:
                return json_format.Parse(json.dumps(data), return_type())
            except Exception as e:
                log.exception("Exception while trying to parse json to protocol buffer! Because: %s", str(e))
        else:
            try:
                msg = return_type()
                msg.ParseFromString(data)
                return msg
            except Exception as e:
                log.exception("Exception while trying to parse data to protocol buffer! Because: %s", str(e))
    return wrapper


def serializer(func):
    sig = signature(func)
    parameter_type = list(sig.parameters.values())[1]
    assert parameter_type != sig.empty, \
        "Deserialization function must first argument (not counting self) of protocol buffer type!"
    parameter_type = parameter_type.annotation
    assert hasattr(parameter_type, "SerializeToString"), \
        "Deserialization function seems not to have a valid protocol buffer first argument type!"
    log = get_logger("Serializer")

    @functools.wraps(func)
    async def wrapper(self, msg):
        nonlocal log
        if isinstance(msg, JsonResponse):
            try:
                return json_format.MessageToJson(_process_tupple(msg.data))
            except Exception as e:
                print(msg.data)
                log.exception("Exception while trying to serialize protocol buffer to json! Because: %s", str(e))
        else:
            try:
                return _process_tupple(msg).SerializeToString()
            except Exception as e:
                log.exception("Exception while trying to serialize protocol buffer! Because: %s", str(e))
    return wrapper
