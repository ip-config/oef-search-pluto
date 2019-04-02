import asyncio
from inspect import signature
import struct
import functools
from network.src.proto import message_pb2
from typing import List
from api.src.python.Interfaces import DataWrapper


# POSIX error codes: http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/errno.h.html

class Transport:
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._int_size = len(struct.pack("i", 0))

    async def write_msg(self, msg: message_pb2.Message):
        smsg = msg.SerializeToString()
        size_packed = struct.pack("i", len(smsg))
        await self.drain()
        self._writer.write(size_packed)
        await self.drain()
        self._writer.write(smsg)

    async def write(self, data: bytes, path: str = ""):
        msg = message_pb2.Message()
        msg.uri = path
        msg.body = data
        msg.status.success = True
        await self.write_msg(msg)

    async def write_error(self, error_code: int, narrative: List[str], path: str = ""):
        msg = message_pb2.Message()
        msg.uri = path
        msg.status.success = False
        msg.status.error_code = error_code
        msg.status.narrative.extend(narrative)
        await self.write_msg(msg)

    async def drain(self):
        return await self._writer.drain()

    async def _read_size(self) -> int:
        size_packed = await self._reader.read(self._int_size)
        if len(size_packed) == 0:
            return 0
        size = struct.unpack("i", size_packed)[0]
        return size

    async def read(self) -> DataWrapper[bytes]:
        try:
            size = await self._read_size()
            if size == 0:
                return DataWrapper(False, "", b'', 104, "Connection closed by peer (got 0 size)")
            data = await self._reader.read(size)
            msg = message_pb2.Message()
            msg.ParseFromString(data)
            if msg.status.success:
                return DataWrapper(True, msg.uri, msg.body)
            else:
                return DataWrapper(False, msg.uri, b'', msg.status.error_code, "", msg.status.narrative[:])
        except ConnectionResetError as e:
            return DataWrapper(False, "", b'', 104, str(e))

    def close(self):
        self._writer.close()


class ClientTransport:
    def __init__(self, transport: Transport):
        self.__transport = transport

    async def write(self, data: bytes, path: str = ""):
        return await self.__transport.write(data, path)

    async def read(self) -> DataWrapper[bytes]:
        return await self.__transport.read()

    async def drain(self):
        return await self.__transport.drain()

    def close(self):
        return self.__transport.close()


def _handler(func):
    async def on_message(reader, writer):
        return await func(Transport(reader, writer))
    return on_message


async def _server(func, host, port):
    server = await asyncio.start_server(_handler(func), host, port)
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
