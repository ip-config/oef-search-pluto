import asyncio
from inspect import signature
import struct
import functools


class Transport:
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer

    def write(self, data: bytes):
        size_packed = struct.pack("I", len(data))
        self._writer.write(size_packed)
        self._writer.write(data)

    async def drain(self):
        return await self._writer.drain()

    async def read(self) -> bytes:
        try:
            size_packed = await self._reader.read(len(struct.pack("I", 0)))
            if len(size_packed) == 0:
                return []
            size = struct.unpack("I", size_packed)[0]
            return await self._reader.read(size)
        except ConnectionResetError:
            return []

    def close(self):
        self._writer.close()


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


async def run_server(handler_func, host, port):
    assert hasattr(handler_func, "__async_socket_handler__"), "Handler function must be annotated with handler!"
    return await _server(handler_func, host, port)


async def run_client(handler_func, host, port):
    assert hasattr(handler_func, "__async_socket_handler__"), "Handler function must be annotated with handler!"
    reader, writer = await asyncio.open_connection(host, port)
    return await handler_func(Transport(reader, writer))
