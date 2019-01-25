from concurrent.futures import ThreadPoolExecutor
import asyncio
from network.src.python.async_socket.AsyncSocket import run_server, handler, Transport
from api.src.proto import query_pb2
from api.src.python.BackendEntryPoint import backend_entry


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


def blocking_socket_loop():
    asyncio.run(run_server(on_connection, "127.0.0.1", 7500))


def blocking_http_loop():
    while True:
        pass


if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(blocking_socket_loop())
    executor.submit(blocking_http_loop())
    executor.shutdown(wait=True)

