import asyncio
from api.proto import query_pb2
from network.src.python.async_socket.AsyncSocket import handler, run_client, Transport


@handler
async def client(transport: Transport):
    msg = query_pb2.Query()
    msg.name = "Client"
    transport.write(msg.SerializeToString())
    response = await transport.read()
    msg.ParseFromString(response)
    print("Response from server: ", msg.name)
    transport.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run_client(client, "127.0.0.1", 7500))
loop.close()
