from concurrent.futures import ThreadPoolExecutor
import asyncio
from network.src.python.async_socket.AsyncSocket import run_server, handler, Transport
from api.src.python.BackendRouter import BackendRouter
from fetch_teams.bottle import SSLWSGIRefServer
from fetch_teams.bottle import bottle
import sys
from utils.src.python.Logging import get_logger, configure as configure_logging
from api.src.python.EndpointSearch import SearchQuery
from api.src.python.EndpointUpdate import UpdateEndpoint
from dap_api.src.python.DapManager import DapManager
import api.src.python.ProtoWrappers as ProtoWrappers


def socket_handler(router: BackendRouter):
    log = get_logger("SocketConnectionHandler")

    @handler
    async def on_connection(transport: Transport):
        log.info("Got socket client")
        path, data = await transport.read()
        response = await router.route(path, data)
        await transport.write(response)
        transport.close()
    return on_connection


def run_socket_server(host: str, port: str, router: BackendRouter):
    asyncio.run(run_server(socket_handler(router), host, port))


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


def run_http_server(host: str, port: int, crt_file: str, router: BackendRouter):
    app = bottle.Bottle()
    srv = SSLWSGIRefServer.SSLWSGIRefServer(host=host, port=port, certificate_file=crt_file)
    app.route(path="/json/<path:path>", method="POST", callback=http_json_handler(router))
    bottle.run(server=srv, app=app)


if __name__ == "__main__":
    configure_logging()

    executor = ThreadPoolExecutor(max_workers=2)
    http_port_number = int(sys.argv[1])
    certificate_file = sys.argv[2]
    socket_port_number = http_port_number+1
    if len(sys.argv) == 4:
        socket_port_number = sys.argv[3]

    #DAPManager
    dap_manager = DapManager()

    dap_manager_config = {
        "search_engine": {
            "class": "SearchEngine",
            "config": {
                "structure": {
                    "dm_store": {
                        "data_model": "dm"
                    }
                }
            }
        }
    }

    dap_manager.setup(sys.modules[__name__], dap_manager_config)

    update_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.UpdateData, {
        "table": "dm_store",
        "field": "data_model"
    })
    query_wrapper = ProtoWrappers.ProtoWrapper(ProtoWrappers.QueryData)

    search_engine = dap_manager.getInstance("search_engine")

    #modules
    search_module = SearchQuery(search_engine, query_wrapper)
    update_module = UpdateEndpoint(search_engine, update_wrapper)

    #router
    router_ = BackendRouter()
    router_.register_serializer("search", search_module)
    router_.register_handler("search", search_module)
    router_.register_serializer("update", update_module)
    router_.register_handler("update", update_module)

    executor.submit(run_socket_server, "0.0.0.0", socket_port_number, router_)
    executor.submit(run_http_server, "0.0.0.0", http_port_number, certificate_file, router_)
    executor.shutdown(wait=True)
