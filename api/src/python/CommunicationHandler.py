from concurrent.futures import ThreadPoolExecutor
import asyncio
from network.src.python.async_socket.AsyncSocket import run_server, handler, Transport
from api.src.proto import query_pb2
from api.src.python.BackendEntryPoint import backend_entry
from third_party.bottle import SSLWSGIRefServer
from third_party.bottle import bottle
import sys
import json
from google.protobuf import json_format


@handler
async def on_connection(transport: Transport):
    print("Got socket client")
    data = await transport.read()
    msg = query_pb2.Query()
    msg.ParseFromString(data)
    response = await backend_entry(msg)
    transport.write(response.SerializeToString())
    await transport.drain()
    transport.close()


def run_socket_server(host, port):
    asyncio.run(run_server(on_connection, host, port))


app = bottle.Bottle()


@app.route("/json", method="POST")
def http_json_handler():
    try:
        query = json_format.Parse(json.dumps(bottle.request.json), query_pb2.Query())
        response = asyncio.run(backend_entry(query))
        bottle.response.headers['Content-Type'] = 'application/json'
        return json_format.MessageToJson(response)
    except bottle.HTTPError as e:
        print("Not valid JSON request: ", e)


def run_http_server(bottle_app, host, port, crt_file):
    app = bottle.Bottle()
    srv = SSLWSGIRefServer.SSLWSGIRefServer(host=host, port=port, certificate_file=crt_file)
    bottle.run(server=srv, app=bottle_app)


if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=2)
    http_port_number = int(sys.argv[1])
    certificate_file = sys.argv[2]
    socket_port_number = http_port_number+1
    if len(sys.argv) == 4:
        socket_port_number = sys.argv[3]
    executor.submit(run_socket_server, "0.0.0.0", socket_port_number)
    executor.submit(run_http_server, app, "0.0.0.0", http_port_number, certificate_file)
    executor.shutdown(wait=True)

