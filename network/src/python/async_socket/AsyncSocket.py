from abc import ABC
from abc import abstractmethod
import asyncio
from asyncio import transports
import functools


class Writer:
    def __init__(self, transport):
        self.__transport = transport

    def write(self, data: bytes):
        self.__transport.write(data)


class SocketEchoProtocol(asyncio.Protocol):

    on_new_data = lambda data, transport: transport.write(data)

    def __init__(self):
        self.transport = None

    def connection_made(self, transport: transports.BaseTransport):
        self.transport = transport
        self.writer    = Writer(transport)

    def data_received(self, data: bytes):
        #stuff here
        SocketEchoProtocol.on_new_data(data, self.writer)


def communication_handler(func):
    SocketEchoProtocol.on_new_data = func

    @functools.wraps
    def wrapper(*args, **argvs):
        pass
    return wrapper


async def server(host, port):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(SocketEchoProtocol, host, port)
    await server.serve_forever()


def run_server(host, port):
    asyncio.run(server(host,port))