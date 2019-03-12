from api.src.python.Interfaces import HasMessageHandler, HasProtoSerializer
from api.src.python.Serialization import serializer, deserializer
from utils.src.python.Logging import has_logger
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.python.DapInterface import DapInterface
from api.src.python.BackendRouter import BackendRouter
from inspect import signature


class DapInterfaceFuncEndpoint(HasMessageHandler, HasProtoSerializer):
    @has_logger
    def __init__(self, dap: DapInterface, func_name: str):
        self.log.update_local_name(dap.__class__.__name__+":"+func_name)
        self._dap_call = getattr(dap, func_name)
        source = signature(self._dap_call)
        source_param = next(enumerate(source.parameters.values()))[1]
        target_sig = signature(self.serialize)
        target_sig = target_sig.replace(return_annotation=source_param.annotation)
        self.serialize.__signature__ = target_sig
        target_sig = signature(self.deserialize)
        fit = enumerate(target_sig.parameters.values())
        self_param = next(fit)[1]
        sec_param = next(fit)[1]
        sec_param = sec_param.replace(annotation=source.return_annotation)
        target_sig = target_sig.replace(parameters=[self_param, sec_param])
        self.deserialize.__signature__ = target_sig

        self.serialize = serializer(self.serialize)
        self.deserialize = deserializer(self.deserialize)

        self.info("Creating endpoint with serializer {} and deserializer {} for method {}".format(
            signature(self.serialize),
            signature(self.deserialize),
            func_name
        ))

    def serialize(self, data: bytes):
        pass

    def deserialize(self, proto_msg) -> bytes:
        pass

    async def handle_message(self, msg):
        error = None
        response = None
        try:
            response = self._dap_call(msg)
        except Exception as e:
            error = dap_interface_pb2.ErrorResponse()
            error.message = str(e)
            self.exception("Exception during DAP call: ", e)
        return error, response


def register_dap_interface_endpoints(router: BackendRouter, dap: DapInterface):
    methods = [func for func in dir(dap) if callable(getattr(dap, func)) and func.find("__") == -1]
    for method in methods:
        endpoint = DapInterfaceFuncEndpoint(dap, method)
        backend.register_serializer(method, endpoint)
        backend.register_handler(method, endpoint)
