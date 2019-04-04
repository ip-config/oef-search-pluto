from api.src.python.BackendRouter import BackendRouter
from utils.src.python.Logging import get_logger
from api.src.python.CommunicationHandler import Transport, run_server, CommunicationHandler, handler, http_server
import asyncio
import functools


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
                    await transport.write(response.data, call_id=request.id)
                else:
                    await transport.write_error(response.error_code, response.narrative, request.uri, call_id=request.id)
                    if response.error_code == 104:
                        break
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


def start_network(router: BackendRouter, ip: str, socket_port: int, http_port: int = -1, ssl_certificate = None, html_dir: str = None, *, logger = None):
    if logger is None:
        logger = get_logger("NetworkInterfaceCreator")
    http_info = ""
    if http_port != -1:
        http_info = " & HTTP interface @ {}:{}".format(ip, http_port)
    logger.info("Starting network interface for router {} @ {}:{}{}".format(router.name, ip, socket_port, http_info))
    threads = 1
    if http_port != -1:
        threads = 2
    com = CommunicationHandler(threads)
    com.add(socket_server, ip, socket_port)
    if http_port != -1:
        com.add(http_server, ip, http_port, ssl_certificate, html_dir=html_dir)
    com.start(router)
    return com


def network_support(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        self.start_network = start_network
        return func(*args, **kwargs)

    return wrapper