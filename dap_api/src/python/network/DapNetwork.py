from api.src.python.BackendRouter import BackendRouter
from api.src.python.CommunicationHandler import Transport, run_server, http_json_handler, CommunicationHandler, handler
import functools
from fetch_teams.bottle import SSLWSGIRefServer
from fetch_teams.bottle import bottle
from dap_api.src.python.network.DapEndpoints import register_dap_interface_endpoints
from dap_api.src.python.DapInterface import DapInterface
import asyncio
from utils.src.python.Logging import get_logger


def socket_handler(router: BackendRouter):
    log = get_logger("SocketConnectionHandler")

    @handler
    async def on_connection(transport: Transport):
        log.info("Got socket client")
        while True:
            try:
                path, data = await transport.read()
                if path == "close" or (path == "" and data == []):
                    break
                response = await router.route(path, data)
                await transport.write(response)
            except Exception:
                log.error("Failed to process request: ", path, ", with data: ")
        log.info("Connection lost")
        transport.close()
    return on_connection


def http_json_handler(router):
    log = get_logger("HttpJsonRequestHandler")

    def on_request(path=""):
        log.info("Got json request over http")
        try:
            response = asyncio.run(router.route(path, bottle.request.json))
            bottle.response.headers['Content-Type'] = 'application/json'
            return response
        except bottle.HTTPError as e:
            log.error("Not valid JSON request: ", e)
    return on_request


def socket_server(host: str, port: str, router: BackendRouter):
    asyncio.run(run_server(socket_handler(router), host, port))


def http_server(host: str, port: int, crt_file: str, router: BackendRouter):
    app = bottle.Bottle()
    srv = SSLWSGIRefServer.SSLWSGIRefServer(host=host, port=port, certificate_file=crt_file)
    app.route(path="/json/<path:path>", method="POST", callback=http_json_handler(router))
    bottle.run(server=srv, app=app)


def network_support(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        dap = args[0]
        router = BackendRouter()
        register_dap_interface_endpoints(router, dap)
        dap._router = router

        def start_network(self, ip, socket_port, http_port=-1, ssl_certificate=None):
            threads = 1
            if http_port != -1:
                threads = 2
            com = CommunicationHandler(threads)
            dap._com = com
            com.add(socket_server, ip, socket_port)
            if http_port != -1:
                com.add(http_server, ip, http_port, ssl_certificate)
            com.start(self._router)
            self._com = com

        def wait(self):
            return self._com.wait()

        setattr(dap, "wait", wait)
        setattr(dap, "start_network", start_network)
        return func(*args, **kwargs)
    return wrapper