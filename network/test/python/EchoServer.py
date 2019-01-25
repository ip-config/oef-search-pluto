from network.src.python.async_socket.AsyncSocket import Transport, handler, run_server
from api.proto import query_pb2
import asyncio


@handler
async def on_connection(transport: Transport):
    print("Got client")
    data = await transport.read()
    msg = query_pb2.Query()
    msg.ParseFromString(data)
    print("Got message from client: ", msg.name)
    msg.name = "Server"
    transport.write(msg.SerializeToString())
    await transport.drain()
    transport.close()

asyncio.run(run_server(on_connection, "127.0.0.1", 7500))
