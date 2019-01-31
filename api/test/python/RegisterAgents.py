import asyncio
from network.src.python.async_socket.AsyncSocket import client_handler, run_client, ClientTransport
from api.src.proto import update_pb2


def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


def set_uri(upd: update_pb2.Update, uri: str):
    agent, oef_core = uri.split(",")
    upd.uri.agent = agent
    upd.uri.oef_core.extend([oef_core])


def create_update(uri: str, name: str, description: str, attributes: list) -> update_pb2.Update:
    upd = update_pb2.Update()
    set_uri(upd, uri)
    upd.data_model.name = name
    upd.data_model.description = description
    upd.data_model.attributes.extend(attributes)
    return upd


def create_blk_update() -> update_pb2.Update.BulkUpdate:

    upd1 = create_update("localhost:8000,WeatherAgent",
                         "weather_data",
                         "All possible weather data.", [
                             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
                             get_attr_b("temperature", "Provides wind speed measurements.", 1),
                             get_attr_b("air_pressure", "Provides wind speed measurements.", 2)
                         ])

    upd2 = create_update("localhost:8000,BookAgent1",
                         "book_data",
                         "Book store data", [
                            get_attr_b("title", "The title of the book", 1),
                            get_attr_b("author", "The author of the book", 3),
                            get_attr_b("release_year", "Release year of the book in the UK", 4),
                            get_attr_b("introduction", "Short introduction by the author.", 3),
                            get_attr_b("rating", "Summary rating of the book given by us.", 0)
                        ])
    upd3 = create_update("localhost:8000,BookAgent2Novel",
                         "book_store_new",
                         "Other bookstore. Focuses on novels.", [
                            get_attr_b("title", "The title of the book", 1),
                            get_attr_b("author", "The author of the book", 3),
                            get_attr_b("ISBN", "That code thing", 4),
                            get_attr_b("price", "We will need a lot of money", 3),
                            get_attr_b("count", "How many do we have", 0),
                            get_attr_b("condition", "Our books are in the best condition", 0)
                        ])
    blk_upd = update_pb2.Update.BulkUpdate()
    blk_upd.list.extend([upd1, upd2, upd3])
    return blk_upd


@client_handler
async def client(transport: ClientTransport):
    msg = create_blk_update()
    await transport.write(msg.SerializeToString(), "update")
    response = await transport.read()
    resp = response_pb2.Response()
    resp.ParseFromString(response)
    print("Response from server: ", resp.name)
    transport.close()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run_client(client, "127.0.0.1", 7501))
finally:
    loop.close()
