from network.src.python.async_socket.AsyncSocket import Transport, handler
import asyncio
from utils.src.python.Logging import get_logger, has_logger
from fake_oef.src.python.lib import ConnectionFactory
from fetch_teams.oef_core_protocol import agent_pb2
from fake_oef.src.python.lib.ConnectionFactory import SupportsConnectionInterface

class OEFSocketAdapter(SupportsConnectionInterface):
    @has_logger
    def __init__(self, core_id, connection_factory: ConnectionFactory):
        self._connection_factory = connection_factory
        self._core = core_id
        self._id = core_id.replace("-core", "-adapter")
        self._connection_factory.add_obj(self._id, self)
        self.con = self._connection_factory.create(core_id, self._id)
        self.handshake_state = 0
        self.agent_id = None
        self.connections = {}

    @property
    def connection(self):
        return self.connections

    @connection.setter
    def connection(self, value):
        self.connections = value

    async def handshake(self, data):
        resp = None
        if self.handshake_state == 0:
            agent_id = agent_pb2.Agent.Server.ID()
            agent_id.ParseFromString(data)
            self.agent_id = agent_id.public_key
            self.log.update_local_name(self._id.replace("-adapter", "") + " - " + self.agent_id)
            resp = agent_pb2.Server.Phrase()
            resp.phrase = "RandomPhrase"
            self.handshake_state = 1
        elif self.handshake_state == 1:
            answer = agent_pb2.Agent.Server.Answer()
            answer.ParseFromString(data)
            self.error("Got handshake phrase answer: ", answer.answer)
            resp = agent_pb2.Server.Connected()
            resp.status = True
            self.handshake_state = 2
        return resp.SerializeToString()

    async def handle_message(self, data: bytes):
        if self.handshake_state != 2:
            return await self.handshake(data)
        envelope = agent_pb2.Envelope()
        envelope.ParseFromString(data)
        self.error("Got data: ", envelope)
        msg = agent_pb2.Server.AgentMessage()
        msg.answer_id = 1

        return b''

    def on_close(self):
        self.con.disconnect()


def socket_message_handler(adapter: OEFSocketAdapter):
    log = get_logger("OEFSocketConnectionHandler")

    async def on_connection(reader, writer):
        log.error("Got socket client")
        transport = Transport(reader, writer)
        while True:
            _, data = await transport.read()
            if len(data) == 0:
                break
            response = await adapter.handle_message(data)
            await transport.write(response)
        adapter.on_close()
        transport.close()
    return on_connection


class OEFSocketAdapterServerBuilder:
    @has_logger
    def __init__(self, connection_factory: ConnectionFactory, host: str):
        self.connection_factory = connection_factory
        self.host = host
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()

    def run_forever(self):
        self.loop.run_forever()

    async def _create_server(self, adapter, port, loop):
        server = await asyncio.start_server(socket_message_handler(adapter), self.host, port, loop=loop)
        return await server.serve_forever()

    def create_socket(self, port: int, core_id: str):
        adapter = OEFSocketAdapter(core_id, self.connection_factory)
        self.loop.create_task(OEFSocketAdapterServerBuilder._create_server(self, adapter, port, self.loop))

    def cancel(self):
        all_tasks = asyncio.all_tasks(loop=self.loop)
        for task in all_tasks:
            task.cancel()
        self.loop.stop()
        self.loop.close()
