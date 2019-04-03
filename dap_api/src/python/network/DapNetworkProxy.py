from dap_api.src.python.DapInterface import DapInterface
from dap_api.src.protos import dap_interface_pb2, dap_update_pb2, dap_description_pb2
from utils.src.python.Logging import has_logger
import struct
import socket
import json
from network.src.proto import transport_pb2
from network.src.python.async_socket.AsyncSocket import DataWrapper
import time
from typing import List, Tuple


class Transport:
    def __init__(self, socket: socket.socket):
        self._socket = socket
        self._int_size = len(struct.pack("i", 0))

    def write_msg(self, msg: transport_pb2.TransportHeader, data: bytes):
        smsg = msg.SerializeToString()
        size_packed = struct.pack("!ii", len(smsg), len(data))
        self._socket.sendall(size_packed)
        self._socket.sendall(smsg)
        self._socket.sendall(data)

    def write(self, data: bytes, path: str = ""):
        msg = transport_pb2.TransportHeader()
        msg.uri = path
        msg.status.success = True
        self.write_msg(msg, data)

    def write_error(self, error_code: int, narrative: List[str], path: str = ""):
        msg = transport_pb2.TransportHeader()
        msg.uri = path
        msg.status.success = False
        msg.status.error_code = error_code
        msg.status.narrative.extend(narrative)
        self.write_msg(msg, b'')

    def _read_size(self) -> Tuple[int, int]:
        size_packed = self._socket.recv(2*self._int_size)
        if len(size_packed) == 0:
            return 0, 0
        sizes = struct.unpack("!ii", size_packed)
        return sizes

    def read(self) -> DataWrapper[bytes]:
        msg = None
        try:
            hsize, bsize = self._read_size()
            if hsize == 0:
                return DataWrapper(False, "", b'', 104, "Connection reset (got 0 size)")
            data = self._socket.recv(hsize+bsize)
            msg = transport_pb2.TransportHeader()
            msg.ParseFromString(data[:hsize])
            if msg.status.success:
                return DataWrapper(True, msg.uri, data[hsize:])
            else:
                return DataWrapper(False, msg.uri, b'', msg.status.error_code, "", msg.status.narrative[:])
        except ConnectionResetError as e:
            return DataWrapper(False, msg.uri if msg else "", b'', 104, str(e))

    def close(self):
        self.write(b'', "close")
        self._socket.close()


class ClientSocket:
    def __init__(self, host: str, port: int, logger):
        self.transport = None
        self.host = host
        self.port = port
        self._socket = None
        self.log = logger
        self.connect()
        self._call_max_depth = 10

    def connect(self):
        self._socket = socket.socket(socket.AF_INET)
        self._socket.connect((self.host, self.port))
        self.log.info("Connected to network dap!")
        self.transport = Transport(self._socket)

    def close(self):
        self.transport.close()

    def call(self, func, in_data, depth=0):
        try:
            self.transport.write(in_data, func)
            return self.transport.read()
        except BrokenPipeError as e:
            self.warning("Connection lost with host %s:%d, reconnecting...", self.host, self.port)
            if depth > self._call_max_depth:
                return DataWrapper(False, func, b'', 32, str(e))
            time.sleep(0.5*depth)
            self.connect()
            return self.call(func, in_data, depth+1)


class DapNetworkProxy(DapInterface):
    @has_logger
    def __init__(self, name, configuration):
        self.host = configuration["host"]
        self.port = configuration["port"]
        self.log.update_local_name(name+"@"+self.host+":"+str(self.port))
        self.info("Opening connection...")
        self.client = ClientSocket(self.host, self.port, self.log)

    def inject_w2v(self, *args, **kwargs):
        pass

    def close(self):
        self.client.close()

    def _call(self, path, data_in, output_type):
        response = self.client.call(path, data_in.SerializeToString())
        proto = output_type()
        if not response.success:
            self.error("Error response for uri %s, code: %d, reason: %s", response.uri, response.error_code,
                       response.msg())
            return proto
        try:
            proto.ParseFromString(response.data)
        except:
            try:
                sproto = dap_interface_pb2.Successfulness()
                sproto.ParseFromString(response.data)
                if not sproto.success:
                    self.error("Dap failure: code %d, message: %s", sproto.errorcode, sproto.narrative)
                else:
                    self.error("Unknown failure! Message: %s", sproto.message)
            except:
                self.exception("Unknown error!")
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
        return self._call("execute", proto, dap_interface_pb2.IdentifierSequence)


def _config_from_dap_json(file, cls = "DapNetworkProxy"):
    f = open(file)
    j = json.load(f)

    config = dict()
    c = config[j["description"]["name"]] = dict()

    if cls is None:
        cls = j["class"]

    c["class"] = cls
    c["config"] = dict()
    c["config"]["host"] = j["host"]
    c["config"]["port"] = j["port"]
    c["config"]["structure"] = dict()

    cs = c["config"]["structure"]

    tb = j["description"]["table"]
    if tb:
        cs[tb["name"]] = dict()
        for f in tb["field"]:
            cs[tb["name"]][f["name"]] = f["type"]
    return config


def proxy_config_from_dap_json(file):
    return _config_from_dap_json(file)


def config_from_dap_json(file):
    return _config_from_dap_json(file, None)
