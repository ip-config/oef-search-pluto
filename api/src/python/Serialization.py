import functools
from inspect import signature
from google.protobuf import json_format
import json
from utils.src.python.Logging import get_logger
from enum import Enum
from typing import Any

def _process_tupple(data):
    if isinstance(data, tuple):
        if data[0] is None:
            return data[1]
        else:
            return data[0]
    else:
        return data


class Serializable:
    class TargetType(Enum):
        PROTO = 1,
        JSON = 2

    def __init__(self, proto: Any, target_type: TargetType = TargetType.PROTO):
        self.proto = proto
        self.target_type = target_type


def deserializer(func):
    sig = signature(func)
    return_type = sig.return_annotation
    assert return_type != sig.empty, \
        "Deserialization function must have a protocol buffer return type!"
    assert hasattr(return_type, "ParseFromString"), \
        "Deserialization function seems not to have a valid protocol buffer return type!"
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
            msg = return_type()
            try:
                msg.ParseFromString(data)
                return msg
            except Exception as e:
                log.exception("Exception while trying to parse data to protocol buffer! Because: %s", str(e))
                return msg
    return wrapper


def serializer(func):
    sig = signature(func)
    parameter_type = list(sig.parameters.values())[1]
    assert parameter_type != sig.empty, \
        "Serialization function must first argument (not counting self) of protocol buffer type!"
    parameter_type = parameter_type.annotation
    assert hasattr(parameter_type, "SerializeToString"), \
        "Serialization function seems not to have a valid protocol buffer first argument type!"
    log = get_logger("Serializer")

    @functools.wraps(func)
    async def wrapper(self, msg: Serializable):
        nonlocal log
        if msg.target_type == Serializable.TargetType.JSON:
            try:
                return json_format.MessageToJson(_process_tupple(msg.proto))
            except Exception as e:
                log.exception("Exception while trying to serialize protocol buffer to json! Because: ", str(e))
                print("Serializer got data: ", msg.proto)
        else:
            try:
                return _process_tupple(msg.proto).SerializeToString()
            except Exception as e:
                log.exception("Exception while trying to serialize protocol buffer! Because: %s", str(e))
                print("Serializer got data: ", msg.proto)
        return b''
    return wrapper
