from api.src.python.BackendRouter import BackendRouter
from api.src.python.CommunicationHandler import socket_server, http_json_handler, CommunicationHandler
import functools
from fetch_teams.bottle import SSLWSGIRefServer
from fetch_teams.bottle import bottle
from dap_api.src.python.network.DapEndpoints import register_dap_interface_endpoints
from dap_api.src.python.DapInterface import DapInterface


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
