import functools
import abc
import asyncio
from network.src.python.async_socket.AsyncSocket import Transport
from utils.src.python.Logging import has_logger


class Connection(object):
    @has_logger
    def __init__(self, target_ip: str, target_port: int):
        self._host = target_ip
        self._port = target_port
        self._transport = None
        self.log.update_local_name(target_ip+":"+str(target_port))

    async def connect(self):
        self.info("Connecting to {}:{}...".format(self._host, self._port))
        r, w = await asyncio.open_connection(self._host, self._port)
        self.info("Connecting to {}:{}... DONE".format(self._host, self._port))
        self._transport = Transport(r, w)

    def disconnect(self):
        if self._transport:
            self._transport.close()
        self._transport = None

    async def call_node(self, path: str, data: bytes) -> bytes:
        try:
            if self._transport is None:
                await self.connect()
            call_id = await self._transport.write(data, path)
            await self._transport.drain()
            response = await self._transport.read(call_id)
            if not response.success:
                self.error("Error response for uri %s (%s), code: %d, reason: %s", response.uri, path,
                            response.error_code, response.msg())
            return response
        except RuntimeError as e:
            #TODO(AB): fix, hack for different loop error. Hack: recreate connection in the current loop
            if str(e).find("attached to a different loop") != -1:
                self.error("Different event loop error hack! ", str(e))
                self._transport.close()
                self._transport = None
                return await self.call_node(path, data)
            self.exception("Error: ", str(e), type(e))
            raise e
