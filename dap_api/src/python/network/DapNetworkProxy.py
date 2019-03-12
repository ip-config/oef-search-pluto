from dap_api.src.python.DapInterface import DapInterface
import asyncio
from dap_api.src.protos import dap_interface_pb2


class DapNetworkProxy(DapInterface):
    def __init__(self, host: str, port: int):
        reader, writer = await asyncio.open_connection(host, port)


    def describe(self):
        pass

    def update(self, update_data):
        pass

    def remove(self, remove_data):
        pass

    def removeAll(self, key):
        pass

    def prepareConstraint(self,
                          proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        pass

    def prepare(self,
                dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> dap_interface_pb2.ConstructQueryMementoResponse:
        return None

    def execute(self, proto: dap_interface_pb2.ConstructQueryMementoResponse,
                input_idents: dap_interface_pb2.IdentifierSequence) -> dap_interface_pb2.IdentifierSequence:
        pass