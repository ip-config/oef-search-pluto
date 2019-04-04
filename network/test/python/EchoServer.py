from network.src.python.async_socket.AsyncSocket import Transport, handler, run_server
from api.src.proto.core import query_pb2
import asyncio


@handler
async def on_connection(transport: Transport):
    print("Got client")
    response = await transport.read()
    if not response.success:
        print("Error response for uri %s, code: %d, reason: %s", response.uri, response.error_code,
              response.msg())
        return
    msg = query_pb2.Query()
    msg.ParseFromString(response.data)
    print("Got message from client: ", msg.name)
    msg.name = "Server"
    await transport.write(msg.SerializeToString())
    await transport.drain()
    transport.close()

asyncio.run(run_server(on_connection, "127.0.0.1", 7500))
