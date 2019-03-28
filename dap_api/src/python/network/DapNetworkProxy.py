from dap_api.src.python.DapInterface import DapInterface
from dap_api.src.protos import dap_interface_pb2, dap_update_pb2, dap_description_pb2
from utils.src.python.Logging import has_logger
import struct
import socket
import json


class Transport:
    def __init__(self, socket: socket.socket):
        self._socket = socket
        self._int_size = len(struct.pack("i", 0))

    def write(self, data: bytes, path: str = ""):
        if len(path) > 0:
            set_path_cmd = struct.pack("i", -len(path))
            self._socket.sendall(set_path_cmd)
            self._socket.sendall(path.encode())
        size_packed = struct.pack("i", len(data))
        self._socket.sendall(size_packed)
        self._socket.sendall(data)

    def _read_size(self) -> int:
        size_packed = self._socket.recv(self._int_size)
        if len(size_packed) == 0:
            return 0
        size = struct.unpack("i", size_packed)[0]
        return size

    def read(self) -> tuple:
        try:
            size = self._read_size()
            if size == 0:
                return "", []
            path = ""
            if size < 0:
                path = self._socket.recv(-size)
                path = path.decode()
                path = path.replace("\f", "")
                size = self._read_size()
            return path, self._socket.recv(size)
        except ConnectionResetError:
            return "", []

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

    def connect(self):
        self._socket = socket.socket(socket.AF_INET)
        self._socket.connect((self.host, self.port))
        self.log.info("Connected to network dap!")
        self.transport = Transport(self._socket)

    def close(self):
        self.transport.close()

    def call(self, func, in_data):
        try:
            self.transport.write(in_data, func)
            path, data = self.transport.read()
        except BrokenPipeError:
            self.warning("Connection lost with host %s:%d, reconnecting...", self.host, self.port)
            self.connect()
            return self.call(func, in_data)
        return data


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
        resp = self.client.call(path, data_in.SerializeToString())
        try:
            proto = output_type()
            proto.ParseFromString(resp)
        except:
            try:
                sproto = dap_interface_pb2.Successfulness()
                sproto.ParseFromString(resp)
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
