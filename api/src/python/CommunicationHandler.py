from api.src.python.BackendRouter import BackendRouter
import asyncio
from fetch_teams.bottle import SSLWSGIRefServer
from fetch_teams.bottle import bottle
from network.src.python.async_socket.AsyncSocket import run_server, handler, Transport
from utils.src.python.Logging import get_logger
from functools import partial
import utils.src.python.resources as resources
import os
from concurrent.futures import ThreadPoolExecutor
from utils.src.python.Logging import has_logger


_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)


def socket_handler(router: BackendRouter):
    log = get_logger("SocketConnectionHandler")

    @handler
    async def on_connection(transport: Transport):
        log.info("Got socket client")
        request = await transport.read()
        if not request.success:
            log.error("Error response for uri %s, code: %d, reason: %s", request.uri, request.error_code,
                      request.msg())
            return
        response = await router.route(request.uri, request.data)
        if response.success:
            await transport.write(response.data, request.uri, call_id=request.id)
        else:
            await transport.write_error(response.error_code, response.narrative, request.uri, call_id=request.id)
        transport.close()
    return on_connection


def http_json_handler(router):
    log = get_logger("HttpJsonRequestHandler")

    def on_request(path=""):
        global _loop
        log.info("Got json request over http")
        try:
            response = _loop.run_until_complete(router.route(path, bottle.request.json))
            bottle.response.headers['Content-Type'] = 'application/json'
            return response.data
        except bottle.HTTPError as e:
            log.error("Not valid JSON request: ", e)
    return on_request


def socket_server(host: str, port: str, router: BackendRouter):
    global _loop
    _loop.create_task(run_server(socket_handler(router), host, port))


def serve_site(html_dir: str, path: str):
    #if path.find(".js") > 0:
    #    bottle.response.headers['Content-Type'] = 'text/javascript'
    #elif path.find(".css") > 0:
    #    bottle.response.headers['Content-Type'] = 'text/css'
    response = ""
    try:
        response = bottle.static_file(resources.textfile(os.path.join(html_dir, path), as_string=True), root="/")
    except Exception as e:
        print("seve_site exception: ", e)
    return response


def http_server(host: str, port: int, crt_file: str, *, router: BackendRouter, html_dir: str = None):
    app = bottle.Bottle()
    srv = SSLWSGIRefServer.SSLWSGIRefServer(host=host, port=port, certificate_file=crt_file)
    app.route(path="/json/<path:path>", method="POST", callback=http_json_handler(router))
    if html_dir is not None:
        app.route(path="/website/<path:path>", method="GET", callback=partial(serve_site, html_dir))
        app.route(path="/", method="GET", callback=partial(serve_site, html_dir, "index.html"))
    bottle.run(server=srv, app=app)


class CommunicationHandler:
    @has_logger
    def __init__(self, max_threads):
        self.handlers = []
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        self._router = None

    def add(self, *args, **kwargs):
        self.handlers.append((args[0], args[1:], kwargs))

    def set_router(self, router: BackendRouter):
        self._router = router

    def start(self, router: BackendRouter):
        for handler in self.handlers:
            self.warning("Start handler: ", handler)
            self.executor.submit(handler[0], *handler[1], **handler[2], router=router)

    def wait(self):
        self.executor.shutdown(wait=True)
