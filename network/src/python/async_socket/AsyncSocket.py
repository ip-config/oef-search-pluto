import asyncio
from inspect import signature
import struct
import functools
from network.src.proto import transport_pb2
from typing import List, Tuple, Any
from api.src.python.Interfaces import DataWrapper
from utils.src.python.Logging import has_logger

# POSIX error codes: http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/errno.h.html


class TransportCallStore:
    @has_logger
    def __init__(self):
        self._data_store = {}
        self._current = 0

    def new_id(self):
        self._current += 1
        return self._current

    def new_id_if0(self, id: int):
        if id == 0:
            return self.new_id()
        return id

    def reset(self):
        self._current = 0
        self._data_store = {}

    def put(self, id: int,  data: DataWrapper[bytes]):
        if id in self._data_store:
            old = self._data_store[id]
            self.warning("Call id ", id, " already in the storage! Stored uri = ",  old.uri, ", body = ", old.data,
                         "; new uri = ", data.uri, ", new body = ", data.data)
        self._data_store[id] = data

    def pop(self, id: int) -> Any:
        if id not in self._data_store:
            return None
        return self._data_store.pop(id)


class Transport:
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._int_size = len(struct.pack("!I", 0))
        self._call_store = TransportCallStore()

    async def write_msg(self, msg: transport_pb2.TransportHeader, data: bytes):
        smsg = msg.SerializeToString()
        size_packed = struct.pack("!II", len(smsg), len(data))
        await self.drain()
        self._writer.write(size_packed)
        await self.drain()
        self._writer.write(smsg)
        await self.drain()
        if len(data) > 0:
            self._writer.write(data)

    async def write(self, data: bytes, path: str = "", call_id: int = 0) -> int:
        msg = transport_pb2.TransportHeader()
        msg.uri = path
        msg.status.success = True
        msg.id = self._call_store.new_id_if0(call_id)
        await self.write_msg(msg, data)
        return msg.id

    async def write_error(self, error_code: int, narrative: List[str], path: str = "", call_id: int = 0) -> int:
        msg = transport_pb2.TransportHeader()
        msg.uri = path
        msg.id = self._call_store.new_id_if0(call_id)
        msg.status.success = False
        msg.status.error_code = error_code
        msg.status.narrative.extend(narrative)
        await self.write_msg(msg, b'')
        return msg.id

    async def drain(self):
        return await self._writer.drain()

    async def _read_size(self) -> Tuple[int, int]:
        size_packed = await self._reader.read(2*self._int_size)
        if len(size_packed) == 0:
            return 0, 0
        hsize, bsize = struct.unpack("!II", size_packed)
        return hsize, bsize

    async def _read(self, size: int):
        data = await self._reader.read(size)
        if len(data) < size:
            return data + await self._read(size-len(data))
        return data

    async def read(self, call_id: int = 0) -> DataWrapper[bytes]:
        if call_id > 0:
            data = self._call_store.pop(call_id)
            if data is not None:
                return data
        try:
            hsize, bsize = await self._read_size()
            if hsize == 0:
                return DataWrapper(False, "", b'', 104, "Connection closed by peer (got 0 size)")
            data = await self._read(hsize+bsize)
            msg = transport_pb2.TransportHeader()
            msg.ParseFromString(data[:hsize])
            if msg.status.success:
                response = DataWrapper(True, msg.uri, data[hsize:], id=msg.id)
            else:
                response = DataWrapper(False, msg.uri, b'', msg.status.error_code, "", msg.status.narrative[:], id=msg.id)
            if call_id != 0 and msg.id != call_id:
                self._call_store.put(call_id, response)
                return await self.read(call_id)
            return response
        except ConnectionResetError as e:
            return DataWrapper(False, "", b'', 104, str(e))

    def close(self):
        self._writer.close()
        self._call_store.reset()


class ClientTransport:
    def __init__(self, transport: Transport):
        self.__transport = transport

    async def write(self, data: bytes, path: str = ""):
        return await self.__transport.write(data, path)

    async def read(self, call_id: int = 0) -> DataWrapper[bytes]:
        return await self.__transport.read(call_id)

    async def drain(self):
        return await self.__transport.drain()

    def close(self):
        return self.__transport.close()


def _handler(func):
    async def on_message(reader, writer):
        return await func(Transport(reader, writer))
    return on_message


async def _server(func, host, port):
    server = await asyncio.start_server(_handler(func), port=port)
    return await server.serve_forever()


def handler(func):
    fsig = signature(func)
    pars = fsig.parameters
    assert len(pars) == 1, "Handler can have only one parameter"
    par = list(pars.values())[0]
    assert par.annotation is Transport, "Handler parameter type must be specified to be Transport!"
    func.__async_socket_handler__ = True

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def client_handler(func):
    fsig = signature(func)
    pars = fsig.parameters
    assert len(pars) == 1, "Handler can have only one parameter"
    par = list(pars.values())[0]
    assert par.annotation is ClientTransport, "Handler parameter type must be specified to be Transport!"
    func.__async_socket_handler__ = True

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


async def run_server(handler_func, host, port):
    assert hasattr(handler_func, "__async_socket_handler__"), "Handler function must be annotated with handler!"
    return await _server(handler_func, host, port)


async def run_client(handler_func, host, port):
    assert hasattr(handler_func, "__async_socket_handler__"), "Handler function must be annotated with handler!"
    reader, writer = await asyncio.open_connection(host, port)
    return await handler_func(ClientTransport(Transport(reader, writer)))
