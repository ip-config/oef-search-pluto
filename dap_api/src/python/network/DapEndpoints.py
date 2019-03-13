from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.python.DapInterface import DapInterface
from api.src.python.BackendRouter import BackendRouter
from inspect import signature, Parameter


class DapInterfaceFuncEndpointBase(HasMessageHandler, HasProtoSerializer):
    @has_logger
    def __init__(self, dap: DapInterface, func_name: str):
        self.log.update_local_name(dap.__class__.__name__+":"+func_name)
        self._dap_call = getattr(dap, func_name)

        self.info("Creating endpoint with serializer {} and deserializer {} for method {}".format(
            signature(self.serialize),
            signature(self.deserialize),
            func_name
        ))

    def serialize(self, proto_msg) -> bytes:
        pass

    def deserialize(self, data: bytes):
        pass

    async def handle_message(self, msg):
        error = None
        response = None
        try:
            if isinstance(msg, dap_interface_pb2.NoInputParameter):
                response = self._dap_call()
            else:
                response = self._dap_call(msg)
        except Exception as e:
            error = dap_interface_pb2.Successfulness()
            error.success = False
            error.errorcode = 503
            error.narrative = str(e)
            self.exception("Exception during DAP call: ", e)
        return error, response


def DapInterfaceFuncEndpointFactory(dap, method):
    EndpointClass = type("DapInterface"+method+"Endpoint", (DapInterfaceFuncEndpointBase,), {})
    source = signature(getattr(dap, method))
    try:
        source_param = next(enumerate(source.parameters.values()))[1]
    except StopIteration:
        source_param = Parameter("proto", Parameter.POSITIONAL_OR_KEYWORD, annotation=dap_interface_pb2.NoInputParameter)

    target_sig = signature(EndpointClass.deserialize)
    target_sig = target_sig.replace(return_annotation=source_param.annotation)
    EndpointClass.deserialize.__signature__ = target_sig

    target_sig = signature(EndpointClass.serialize)
    fit = enumerate(target_sig.parameters.values())
    self_param = next(fit)[1]
    sec_param = next(fit)[1]
    sec_param = sec_param.replace(annotation=source.return_annotation)
    target_sig = target_sig.replace(parameters=[self_param, sec_param])
    EndpointClass.serialize.__signature__ = target_sig

    EndpointClass.serialize = serializer(EndpointClass.serialize)
    EndpointClass.deserialize = deserializer(EndpointClass.deserialize)

    return EndpointClass(dap, method)


def register_dap_interface_endpoints(router: BackendRouter, dap: DapInterface):
    methods = [func for func in dir(DapInterface) if callable(getattr(dap, func)) and func.find("__") == -1]
    for method in methods:
        endpoint = DapInterfaceFuncEndpointFactory(dap, method)
        router.register_serializer(method, endpoint)
        router.register_handler(method, endpoint)
