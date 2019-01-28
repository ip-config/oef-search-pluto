import asyncio
from inspect import signature
import struct
import functools


class Transport:
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._int_size = len(struct.pack("i", 0))

    async def write(self, data: bytes, path: str = ""):
        if len(path) > 0:
            set_path_cmd = struct.pack("i", -len(path))
            await self.drain()
            self._writer.write(set_path_cmd)
            await self.drain()
            self._writer.write(path.encode())
        size_packed = struct.pack("i", len(data))
        await self.drain()
        self._writer.write(size_packed)
        await self.drain()
        self._writer.write(data)

    async def drain(self):
        return await self._writer.drain()

    async def _read_size(self) -> int:
        size_packed = await self._reader.read(self._int_size)
        if len(size_packed) == 0:
            return 0
        size = struct.unpack("i", size_packed)[0]
        return size

    async def read(self) -> tuple:
        try:
            size = await self._read_size()
            if size == 0:
                return "", []
            path = ""
            if size < 0:
                path = await self._reader.read(-size)
                path = path.decode()
                size = await self._read_size()
            return path, await self._reader.read(size)
        except ConnectionResetError:
            return "", []

    def close(self):
        self._writer.close()


class ClientTransport:
    def __init__(self, transport: Transport):
        self.__transport = transport

    async def write(self, data: bytes, path: str = ""):
        return await self.__transport.write(data, path)

    async def read(self) -> bytes:
        res = await self.__transport.read()
        return res[1]

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
