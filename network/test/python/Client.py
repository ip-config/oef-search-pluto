import asyncio
from api.src.proto.core import query_pb2
from network.src.python.async_socket.AsyncSocket import handler, run_client, Transport


@handler
async def client(transport: Transport):
    msg = query_pb2.Query()
    msg.name = "Client"
    await transport.write(msg.SerializeToString())
    response = await transport.read()
    if not response.success:
        print("Error response for uri %s , code: %d, reason: %s", response.uri, response.error_code,
              response.msg())
        return
    msg.ParseFromString(response.data)
    print("Response from server: ", msg.name)
    transport.close()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run_client(client, "127.0.0.1", 7500))
finally:
    loop.close()
