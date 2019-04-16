import asyncio
from network.src.python.async_socket.AsyncSocket import client_handler, run_client, ClientTransport
import argparse
import sys
import functools
from utils.src.python.Logging import get_logger, has_logger
from asyncio import Queue
from typing import Tuple
from api.src.proto.director import core_pb2
from api.src.proto.director import node_pb2
import time
import numpy as np
from typing import List, Tuple


def create_client(ip: str, port: int):
    log = get_logger("Client @ {}:{}".format(ip, port))
    try:
        queue = Queue()
    except Exception as e:
        log.exception(e)
        return

    @client_handler
    async def com_handler(transport: ClientTransport):
        log.info("connected to the server")
        while True:
            log.info("in loop")
            cmd = await queue.get()
            if len(cmd) != 2:
                break
            cmd, data = cmd
            if len(cmd) == 0 or cmd == "close":
                break
            log.info("Sending %s request with data: %s", cmd, str(data))
            call_id = await transport.write(data.SerializeToString(), cmd)
            response = await transport.read(call_id)
            if response.success:
                log.info("Got response: %s", str(response.data))
            else:
                log.warning("Error: code=%d, narrative: %s", response.error_code, response.msg())
        log.info("close connection")
        transport.close()

    return functools.partial(run_client, com_handler, ip, port), queue


def block_if_first_not_found(func=None, *, store_name=None):
    if func is None:
        return functools.partial(block_if_first_not_found, store_name=store_name)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        name = args[1]
        store = getattr(self, store_name)

        rule = lambda x: 5*(1-np.exp(-x*0.05))+0.5
        it = 0
        while True:
            if name in store:
                break
            time.sleep(rule(it))
            print(".")
            it += 1
        return func(*args, **kwargs)
    return wrapper


class Director:
    @has_logger
    def __init__(self):
        self.clients = {}
        self.transports = {}
        self.addresses = {}

    async def add_node(self, ip: str, port: int, name: str = ""):
        if len(name) == 0:
            name = "{}:{}".format(ip, port)
        self.info("Adding node: {} @ {}:{}".format(name, ip, port))
        transport, queue = create_client(ip, port)
        self.clients[name] = queue
        self.info("create task")
        self.transports[name] = asyncio.create_task(transport())
        self.addresses[name] = (ip, port)

    def get_node_names(self):
        return list(self.clients.keys())

    async def push_cmd(self, client_name: str, cmd: str, data):
        try:
            await self.clients[client_name].put((cmd, data))
        except Exception as e:
            self.exception(e)

    def get_address(self, name: str):
        return self.addresses.get(name, ())

    @block_if_first_not_found(store_name="clients")
    async def set_location(self, client_name: str, core_key: str, location: Tuple[float, float]):
        self.info(client_name, ": Set location for core ", core_key, " to ", location)
        data = core_pb2.CoreLocation()
        data.core_key = core_key
        data.location.lon = location[0]
        data.location.lat = location[1]
        await self.push_cmd(client_name, "location", data)

    @block_if_first_not_found(store_name="clients")
    async def add_peers(self, client_name: str, peers: List[Tuple[str, str, int]]):
        data = node_pb2.PeerUpdate()
        for peer in peers:
            p = data.add_peers.add()
            p.name = peer[0]
            p.host = peer[1]
            p.port = int(peer[2])
        await self.push_cmd(client_name, "peer", data)


    #TODO: this is only for the demo
    @block_if_first_not_found(store_name="clients")
    async def send(self, client_name: str, cmd: str, data):
        self.info(client_name, ": Send update: ", data)
        await self.push_cmd(client_name, cmd, data)

    async def close_all(self):
        for key, queue in self.clients.items():
            await queue.put(("close",))

    async def reset(self):
        await self.close_all()
        self.clients = {}
        self.transports = {}
        self.addresses = {}

    async def wait(self):
        for key in list(self.transports.keys()):
            self.info("Waiting for com transport for ", key)
            await self.transports.pop(key)
