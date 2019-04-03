from network.src.proto import transport_pb2
from network.src.python.async_socket.AsyncSocket import DataWrapper, TransportCallStore
import time
from typing import List, Tuple
import struct
import socket


class Transport:
    def __init__(self, socket: socket.socket):
        self._socket = socket
        self._int_size = len(struct.pack("!I", 0))
        self._call_store = TransportCallStore()

    def write_msg(self, msg: transport_pb2.TransportHeader, data: bytes):
        smsg = msg.SerializeToString()
        size_packed = struct.pack("!II", len(smsg), len(data))
        self._socket.sendall(size_packed)
        self._socket.sendall(smsg)
        if len(data) > 0:
            self._socket.sendall(data)

    def write(self, data: bytes, path: str = "", call_id: int = 0):
        msg = transport_pb2.TransportHeader()
        msg.uri = path
        msg.id = self._call_store.new_id_if0(call_id)
        msg.status.success = True
        self.write_msg(msg, data)

    def write_error(self, error_code: int, narrative: List[str], path: str = "", call_id: int = 0):
        msg = transport_pb2.TransportHeader()
        msg.uri = path
        msg.id = self._call_store.new_id_if0(call_id)
        msg.status.success = False
        msg.status.error_code = error_code
        msg.status.narrative.extend(narrative)
        self.write_msg(msg, b'')

    def _read_size(self) -> Tuple[int, int]:
        size_packed = self._socket.recv(2*self._int_size)
        if len(size_packed) == 0:
            return 0, 0
        sizes = struct.unpack("!II", size_packed)
        return sizes

    def _read(self, size: int):
        data = self._socket.recv(size)
        if len(data) < size:
            return data + self._read(size - len(data))
        return data

    def read(self, call_id: int = 0) -> DataWrapper[bytes]:
        if call_id > 0:
            data = self._call_store.pop(call_id)
            if data is not None:
                return data
        msg = None
        try:
            hsize, bsize = self._read_size()
            if hsize == 0:
                return DataWrapper(False, "", b'', 104, "Connection reset (got 0 size)")
            data = self._read(hsize+bsize)
            msg = transport_pb2.TransportHeader()
            msg.ParseFromString(data[:hsize])
            if msg.status.success:
                response = DataWrapper(True, msg.uri, data[hsize:])
            else:
                response = DataWrapper(False, msg.uri, b'', msg.status.error_code, "", msg.status.narrative[:])
            if call_id != 0 and msg.id != call_id:
                self._call_store.put(call_id, response)
                return self.read(call_id)
            return response
        except ConnectionResetError as e:
            return DataWrapper(False, msg.uri if msg else "", b'', 104, str(e))

    def close(self):
        self.write(b'', "close")
        self._socket.close()
        self._call_store.reset()


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
            self.transport.write(in_data, path=func)
            return self.transport.read()
        except BrokenPipeError as e:
            self.warning("Connection lost with host %s:%d, reconnecting...", self.host, self.port)
            if depth > self._call_max_depth:
                return DataWrapper(False, func, b'', 32, str(e))
            time.sleep(0.5*depth)
            self.connect()
            return self.call(func, in_data, depth+1)