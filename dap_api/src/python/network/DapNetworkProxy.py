from dap_api.src.python.DapInterface import DapInterface
import asyncio
from dap_api.src.protos import dap_interface_pb2, dap_update_pb2, dap_description_pb2
from network.src.python.async_socket.AsyncSocket import Transport
from utils.src.python.Logging import has_logger


class ClientSocket:
    @has_logger
    def __init__(self, host: str, port: int):
        self.transport = None
        self.host = host
        self.port = port
        asyncio.run(self.connect())

    async def connect(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self.transport = Transport(reader, writer)

    def close(self):
        self.transport.close()

    async def acall(self, func, in_data):
        await self.transport.write(in_data, func)
        await self.transport.drain()
        path, data = await self.transport.read()
        if path == "" and len(data) == 0:
            self.warning("Connection lost with host %s:%d, reconnecting...", self.host, self.port)
            await self.connect()
            return await self.acall(func, in_data)
        return data

    def call(self, func, in_data):
        return asyncio.run(self.acall(func, in_data))


class DapNetworkProxy(DapInterface):
    @has_logger
    def __init__(self, name, configuration):
        host = configuration["host"]
        port = configuration["port"]
        self.log.update_local_name(name+"@"+host+":"+str(port))
        self.client = ClientSocket(host, port)

    def close(self):
        self.client.close()

    def _call(self, path, data_in, output_type):
        resp = self.client.call(path, data_in.SerializeToString())
        try:
            proto = output_type()
            proto.ParseFromString(resp)
        except:
            sproto = dap_interface_pb2.Successfulness()
            sproto.ParseFromString(resp)
            if not sproto.successfull:
                self.error("Dap failure: code %d, message: %s", sproto.errorcode, sproto.narrative)
            else:
                self.error("Unknown failure! Message: %s", sproto.message)
        return proto

    def describe(self) -> dap_description_pb2.DapDescription:
        data_in = dap_interface_pb2.NoInputParameter()
        return self._call("describe", data_in, dap_description_pb2.DapDescription)


    """This function will be called with any update to this DAP.

    Args:
      update (dap_update_pb2.DapUpdate): The update for this DAP.

    Returns:
      None
    """

    def update(self, update_data: dap_update_pb2.DapUpdate) -> dap_interface_pb2.Successfulness:
        return self._call("update", update_data, dap_interface_pb2.Successfulness)


    """This function will be called when the core wants to remove data from search

    Args:
        remove_data (dap_update_pb2.DapUpdate): The data which needs to be removed

    Returns:
      None
    """

    def remove(self, remove_data: dap_update_pb2.DapUpdate) -> dap_interface_pb2.Successfulness:
        return self._call("remove", remove_data, dap_interface_pb2.Successfulness)

    """Remove all the keys in the update[].key fields from the store.

        Args:
          remove_data(dap_update_pb2.DapUpdate): The update containing removal keys

        Returns:
          bool success indicator
        """

    def prepareConstraint(self,
                          proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        return self._call("prepareConstraint", proto, dap_interface_pb2.ConstructQueryMementoResponse)

    def prepare(self,
                proto: dap_interface_pb2.ConstructQueryObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        return self._call("prepare", proto, dap_interface_pb2.ConstructQueryMementoResponse)

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        self._call("execute", proto, dap_interface_pb2.IdentifierSequence)

    """This function will be called with parts of the query's AST. If
    the interface can construct a unified query for the whole subtree
    it may do so.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      Either a suitable SubQueryInterface object, or None to let the DapManager handle things.
    """

    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
        return None

    """This function will be called with leaf nodes of the query's
    AST.  The result should be a SubQueryInterface for the constraint object
    object OR None if the constraint cannot be matched.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      Either a suitable QueryExecutionInterface object, or None to let the DapManager handle things.
    """

    def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
        raise Exception("BAD: constructQueryConstraintObject")
