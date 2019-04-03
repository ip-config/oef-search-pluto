from api.src.python.BackendRouter import BackendRouter
from api.src.python.CommunicationHandler import Transport, run_server, CommunicationHandler, handler, http_server
import functools
from fetch_teams.bottle import SSLWSGIRefServer
from fetch_teams.bottle import bottle
from dap_api.src.python.network.DapEndpoints import register_dap_interface_endpoints
from dap_api.src.python.DapInterface import DapInterface
import asyncio
from utils.src.python.Logging import get_logger
import utils.src.python.resources as resources


def socket_handler(router: BackendRouter):
    log = get_logger("DAPSocketConnectionHandler")

    @handler
    async def on_connection(transport: Transport):
        log.info("Got socket client")
        while True:
            try:
                request = await transport.read()
                if not request.success:
                    log.error("Error response for uri %s, code: %d, reason: %s", request.uri, request.error_code,
                              request.msg())
                    break
                response = await router.route(request.uri, request.data)
                if response.success:
                    await transport.write(response.data)
                else:
                    await transport.write_error(response.error_code, response.narrative, request.uri)
            except Exception as e:
                path = request.uri if request else ""
                msg = "Failed to process request for path: " + path + ", because: " + str(e)
                log.exception(msg + "! Received data: " + str(request.data))
                await transport.write_error(response.error_code, [msg], path)
        log.info("Connection lost")
        transport.close()
    return on_connection


def socket_server(host: str, port: str, router: BackendRouter):
    asyncio.run(run_server(socket_handler(router), host, port))


def network_support(func=None, *, router_name=None):
    """
        Adds network support for a class. If router_name is not set, then it will create a router
        which will route DapInterface to the decorated class thus the decorated class must implement the DapInterface.

        If router_name is set then it will use that as router and the class doesn't have to implement DapInterface.
        Its very important that the router_name attribute should be set before calling start_network!
    """
    if func is None:
        return functools.partial(network_support, router_name=router_name)

    router_attr_name = router_name if router_name is not None else "__dap_interface_router"

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        dap = args[0]
        if router_attr_name == "__dap_interface_router":
            router = BackendRouter()
            register_dap_interface_endpoints(router, dap)
            setattr(dap, router_attr_name, router)

        def start_network(self, ip: str, socket_port: int, http_port: int = -1, ssl_certificate: str = None, html_dir: str = None):
            self.info("Starting network interface @ {}:{}".format(ip, socket_port))
            threads = 1
            if http_port != -1:
                threads = 2
            com = CommunicationHandler(threads)
            dap._com = com
            com.add(socket_server, ip, socket_port)
            if http_port != -1:
                com.add(http_server, ip, http_port, ssl_certificate, html_dir=html_dir)
            com.start(getattr(self, router_attr_name))
            self._com = com

        def wait(self):
            return self._com.wait()

        setattr(dap, "wait", wait)
        setattr(dap, "start_network", start_network)
        return func(*args, **kwargs)
    return wrapper
