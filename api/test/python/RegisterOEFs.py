import asyncio
from network.src.python.async_socket.AsyncSocket import client_handler, run_client, ClientTransport
from api.src.proto import update_pb2, response_pb2
from fetch_teams.oef_core_protocol import query_pb2
import argparse
import sys


def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


def create_update(key: str, name: str, description: str, attributes: list) -> update_pb2.Update:
    upd = update_pb2.Update()
    upd.key = key.encode("utf-8")
    dm = query_pb2.Query.DataModel()
    dm.name = name
    dm.description = description
    dm.attributes.extend(attributes)
    dm_instance = update_pb2.Update.DataModelInstance()
    dm_instance.key = upd.key
    dm_instance.model.CopyFrom(dm)
    upd.data_models.extend([dm_instance])
    return upd


def create_address_attribute_update(key: str, ip: str, port: int):
    attr = update_pb2.Update.Attribute()
    key = key.encode("utf-8")
    attr.name = update_pb2.Update.Attribute.Name.Value("NETWORK_ADDRESS")
    attr.value.type = 10
    attr.value.a.ip = ip
    attr.value.a.port = port
    attr.value.a.key = key
    attr.value.a.signature = "Signed".encode("utf-8")
    upd = update_pb2.Update()
    upd.key = key
    upd.attributes.extend([attr])
    return upd


def create_blk_update(flag="") -> update_pb2.Update.BulkUpdate:

    upd1 = create_update("oef:Weather"+flag,
                         "weather_data",
                         "All possible weather data.", [
                             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
                             get_attr_b("temperature", "Provides wind speed measurements.", 1),
                             get_attr_b("air_pressure", "Provides wind speed measurements.", 2)
                         ])

    upd2 = create_update("oef:Books"+flag,
                         "book_data",
                         "Book store data", [
                            get_attr_b("title", "The title of the book", 1),
                            get_attr_b("author", "The author of the book", 3),
                            get_attr_b("release_year", "Release year of the book in the UK", 4),
                            get_attr_b("introduction", "Short introduction by the author.", 3),
                            get_attr_b("rating", "Summary rating of the book given by us.", 0)
                        ])
    upd3 = create_update("oef:Novels"+flag,
                         "book_store_new",
                         "Other bookstore. Focuses on novels.", [
                            get_attr_b("title", "The title of the book", 1),
                            get_attr_b("author", "The author of the book", 3),
                            get_attr_b("ISBN", "That code thing", 4),
                            get_attr_b("price", "We will need a lot of money", 3),
                            get_attr_b("count", "How many do we have", 0),
                            get_attr_b("condition", "Our books are in the best condition", 0)
                        ])
    upd4 = create_address_attribute_update("oef:Weather"+flag, "127.0.0.1", 3333)
    upd5 = create_address_attribute_update("oef:Books"+flag, "127.0.0.1", 3334)
    upd6 = create_address_attribute_update("oef:Novels"+flag, "127.0.0.1", 3335)
    blk_upd = update_pb2.Update.BulkUpdate()
    blk_upd.list.extend([upd1, upd2, upd3, upd4, upd5, upd6])
    return blk_upd

parser = argparse.ArgumentParser()
parser.add_argument("--id", required=True, type=int)
args = parser.parse_args()
ID = args.id
print("ID", ID)

@client_handler
async def client(transport: ClientTransport):
    global ID
    print("connected to the server")
    msg = create_blk_update(str(ID))
    await transport.write(msg.SerializeToString(), "blk_update")
    response = await transport.read()
    if not response.success:
        print("Error response for uri %s, code: %d, reason: %s", response.uri, response.error_code, response.msg())
        return
    resp = response_pb2.UpdateResponse()
    resp.ParseFromString(response.data)
    print("Response from server: ", resp.status)
    transport.close()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run_client(client, "127.0.0.1", 20000+ID))
finally:
    loop.close()
