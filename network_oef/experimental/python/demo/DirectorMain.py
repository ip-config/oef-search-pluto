from api.experimental.python.Director import Director
import argparse
from typing import List
import asyncio
from api.experimental.python.DemoWeatherAgent import create_blk_update as create_weather_agent_service
from england_grid.src.python.lib import EnglandGrid
import sys
import socket
import time


def get_core_names(grid=None):
    if grid is None:
        grid = EnglandGrid.EnglandGrid()
        grid.load()
    core_names = []
    for key, entity in grid.entities.items():
        if entity.kind != "CITY":
            continue
        core_names.append((entity.name, entity.attributes["pop"]))
    core_names = map(lambda x: x[0], sorted(core_names, key=lambda x: x[1], reverse=True))
    return core_names


async def set_nodes(director: Director, addresses: List[str]):
    names = get_core_names()
    for address in addresses:
        host, port = address.split(":")
        try:
            host = socket.gethostbyname(host)
        except Exception as e:
            print("Resolution failed, because: " + str(e))
            return False
        port = int(port)
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex((host, port)) == 0:
                break
            print(".")
            time.sleep(2)
        name = next(names)
        await director.add_node(host, port, name)


async def set_weather_agents(director: Director):
    names = director.get_node_names()
    tasks = []
    core_names = get_core_names()
    for name in names:
        host, port = name.split(":")
        if host.find("oef_node") != -1:
            i = int(host.replace("oef_node", ""))
        else:
            i = int(port)-20000
        core_name = next(core_names)
        task = asyncio.create_task(director.send(name, "blk_update",
                                                 create_weather_agent_service(10000+i, core_name)))
        tasks.append(task)
    for task in tasks:
        await task


async def set_locations(director: Director):
    grid = EnglandGrid.EnglandGrid()
    grid.load()
    core_names = get_core_names(grid)
    i = 0
    names = director.get_node_names()
    for key, entity in grid.entities.items():
        if entity.kind != "CITY":
            continue
        print("SET LOCATION {} NODE TO {}".format(names[i], entity.name))
        core_name = next(core_names)
        await director.set_location(names[i], core_name.encode("UTF-8"), (entity.coords[1], entity.coords[0])) #lon, lat
        i += 1
        if i >= len(names):
            break


async def set_locations_and_connections(director: Director):
    grid = EnglandGrid.EnglandGrid()
    grid.load()

    core_names = get_core_names(grid)

    peers = {}
    addresses = {}
    i = 0
    for key, entity in grid.entities.items():
        if entity.kind != "CITY":
            continue
        core_name = next(core_names)
        a = director.get_address(core_name)
        if len(a) == 0:
            continue
        print("SET LOCATION {}@{}:{} NODE TO {}".format(core_name, a[0], a[1], entity.name))
        addresses[core_name] = a
        peers[core_name] = [link[0].name for link in entity.links if link[1] == "GND"]
        await director.set_location(core_name, core_name.encode("utf-8"), (entity.coords[1], entity.coords[0])) #lon, lat
    for key in peers:
        targets = [(peer, *addresses[peer]) for peer in peers[key] if peer in addresses]
        print("ADD PEERS for core {}: ".format(key), targets)
        await director.add_peers(key, targets)


async def main(args):
    director = Director()

    await set_nodes(director, args.targets)

    if args.type == "location":
        await set_locations(director)
    elif args.type == "weather_agent":
        await set_weather_agents(director)
    elif args.type == "location_and_connection":
        await set_locations_and_connections(director)
    else:
        print("Command type {} not supported!".format(args.type))

    await director.close_all()

    await director.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DEMO Director')
    parser.add_argument("--targets", nargs='+',  type=str, help="Node addresses host:port ...")
    parser.add_argument("--type", type=str, required=True, help="weather_agent/location/location_and_connection")
    args_ = parser.parse_args()

    asyncio.run(main(args_))

