import asyncio


async def com():
    reader, writer = await asyncio.open_connection("localhost", 7500)
    writer.write(b"Hello")
    resp = await reader.read(5)
    print("Got response: ", resp)
    writer.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(com())
loop.close()
