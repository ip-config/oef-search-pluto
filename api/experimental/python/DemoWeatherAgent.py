from api.experimental.python.Director import Director
from utils.src.python.Logging import configure
import asyncio
import argparse
from fetch_teams.oef_core_protocol import query_pb2
from api.src.proto.core import update_pb2


def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


def create_update(key: str, agent: str, name: str, description: str, attributes: list) -> update_pb2.Update:
    upd = update_pb2.Update()
    upd.key = key.encode("utf-8")
    dm = query_pb2.Query.DataModel()
    dm.name = name
    dm.description = description
    dm.attributes.extend(attributes)
    dm_instance = update_pb2.Update.DataModelInstance()
    dm_instance.key = agent.encode("utf-8")
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


def create_blk_update(port: int, core_name: str = "") -> update_pb2.Update.BulkUpdate:
    if len(core_name) == 0:
        core_name = "oef:Weather"+str(port)
    upd1 = create_update(core_name,
                         "Agent"+str(port),
                         "weather_data",
                         "All possible weather data.", [
                             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
                             get_attr_b("temperature", "Provides wind speed measurements.", 1),
                             get_attr_b("air_pressure", "Provides wind speed measurements.", 2)
                         ])
    upd2 = create_address_attribute_update(core_name, "127.0.0.1", port)
    blk_upd = update_pb2.Update.BulkUpdate()
    blk_upd.list.extend([upd1, upd2])
    return blk_upd


async def set_nodes(director: Director, port_start: int, port_end: int):
    num = port_end-port_start+1
    for i in range(num):
        await director.add_node("127.0.0.1", port_start+i, str(i))


async def set_weather_agents(director: Director):
    i = 0
    names = director.get_node_names()
    for name in names:
        await director.send(name, "blk_update", create_blk_update(3333+i))
        i += 1


async def main(args):
    configure()
    director = Director()

    await set_nodes(director, args.port_start, args.port_end)

    await set_weather_agents(director)

    await director.close_all()

    await director.wait()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--port_start", required=True, type=int)
    parser.add_argument("--port_end", required=True, type=int)
    asyncio.run(main(parser.parse_args()))
