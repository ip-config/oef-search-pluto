from network.src.python.async_socket.AsyncSocket import Transport, handler
import asyncio
from utils.src.python.Logging import get_logger, has_logger
from fake_oef.src.python.lib import ConnectionFactory
from fetch_teams.oef_core_protocol import agent_pb2
from fake_oef.src.python.lib.ConnectionFactory import SupportsConnectionInterface
from api.src.proto import query_pb2


class ComSession:
    def __init__(self):
        self._auth_status = 0
        self.agent_id = None

    def authenticated(self):
        return self._auth_status == 2

    def first_contact(self):
        return self._auth_status == 0

    def waiting_for_phrase(self):
        return self._auth_status == 1

    def set_agent_id(self, agent_id):
        self.agent_id = agent_id
        self._auth_status = 1

    def get_phrase(self):
        return "RandomPhrase"

    def verify(self, phrase):
        self._auth_status = 2
        return True


class OEFSocketAdapter(SupportsConnectionInterface):
    @has_logger
    def __init__(self, core_id, connection_factory: ConnectionFactory):
        self._connection_factory = connection_factory
        self._core = core_id
        self._id = core_id.replace("-core", "-adapter")
        self._connection_factory.add_obj(self._id, self)
        self.com = self._connection_factory.create(core_id, self._id)
        self.handshake_state = 0
        self.connections = {}

    @property
    def connection(self):
        return self.connections

    @connection.setter
    def connection(self, value):
        self.connections = value

    async def handshake(self, data, session: ComSession):
        resp = None
        if session.first_contact():
            agent_id = agent_pb2.Agent.Server.ID()
            agent_id.ParseFromString(data)
            session.set_agent_id(agent_id.public_key)
            self.log.update_local_name(self._id.replace("-adapter", "") + " - " + session.agent_id)
            resp = agent_pb2.Server.Phrase()
            resp.phrase = session.get_phrase()
        elif session.waiting_for_phrase():
            answer = agent_pb2.Agent.Server.Answer()
            answer.ParseFromString(data)
            self.error("Got handshake phrase answer: ", answer.answer)
            if session.verify(answer.answer):
                resp = agent_pb2.Server.Connected()
                resp.status = True
        return resp.SerializeToString()

    #TODO handle error
    async def handle_message(self, data: bytes, session: ComSession):
        if not session.authenticated():
            return await self.handshake(data, session)
        envelope = agent_pb2.Envelope()
        envelope.ParseFromString(data)
        self.error("Got data: ", envelope)

        resp = agent_pb2.Server.AgentMessage()
        resp.answer_id = envelope.msg_id
        no_answer = True

        case = envelope.WhichOneof("payload")
        if case == "send_message":
            self.error("Case %s not yet supported", case)
        elif case == "register_service":
            try:
                self.error("Register service...")
                await self.com.async_register_service(session.agent_id, envelope.register_service.description)
            except Exception as e:
                self.exception("Failed to register service: ", str(e))
                resp.oef_error.operation = agent_pb2.Server.AgentMessage.OEFError.REGISTER_SERVICE
                no_answer = False
        elif case == "unregister_service":
            self.error("Case %s not yet supported", case)
        elif case == "register_description":
            self.error("Case %s not yet supported", case)
        elif case == "unregister_description":
            self.error("Case %s not yet supported", case)
        elif case == "search_services":
            query = query_pb2.Query()
            query.model.CopyFrom(envelope.search_services.query)
            query.ttl = 2
            qresp = await self.com.async_search(query)
            self.error(qresp)
            for agent in qresp.result:
                resp.agents.agents.append(agent.key.decode("UTF-8"))
            self.error(resp)
            no_answer = False
        elif case == "search_agents":
            self.error("Case %s not yet supported", case)
        if no_answer:
            return b''
        else:
            return resp.SerializeToString()

    def on_close(self):
        self.com.disconnect()


def socket_message_handler(adapter: OEFSocketAdapter):
    log = get_logger("OEFSocketConnectionHandler")

    async def on_connection(reader, writer):
        log.error("Got socket client")
        transport = Transport(reader, writer)
        session = ComSession()
        while True:
            _, data = await transport.read()
            if len(data) == 0:
                break
            response = await adapter.handle_message(data, session)
            await transport.write(response)
        transport.close()
    return on_connection


class OEFSocketAdapterServerBuilder:
    @has_logger
    def __init__(self, connection_factory: ConnectionFactory, host: str):
        self.connection_factory = connection_factory
        self.host = host
        self.adapters = []
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
        self.adapters.append(adapter)

    def cancel(self):
        all_tasks = asyncio.all_tasks(loop=self.loop)
        for task in all_tasks:
            task.cancel()
        self.loop.stop()
        self.loop.close()
        for adapter in self.adapters:
            adapter.on_close()

