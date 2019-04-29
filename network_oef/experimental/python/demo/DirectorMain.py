from api.experimental.python.Director import Director
import argparse
from typing import List
import asyncio
from api.experimental.python.DemoWeatherAgent import create_blk_update as create_weather_agent_service
from england_grid.src.python.lib import EnglandGrid
import sys
import socket
import time
from utils.src.python.Logging import configure as configure_logging
import logging
import json


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


async def set_node(director: Director, host: str, port: str, name: str):
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
    await director.add_node(host, port, name)


async def set_nodes(director: Director, addresses: List[str]):
    names = get_core_names()
    for address in addresses:
        host, port = address.split(":")
        name = next(names)
        await set_node(director, host, port, name)


async def set_weather_agents(director: Director):
    names = director.get_node_names()
    tasks = []
    core_names = get_core_names()
    for name in names:
        host, port = director.get_address(name)
        if host.find("oef_node") != -1:
            i = int(host.replace("oef_node", ""))
        else:
            i = int(port)-20000
        core_name = next(core_names)+"-core"
        print("SET WEATHER AGENT FOR: ", name, "; core_name: ", core_name)
        task = asyncio.create_task(director.send(name, "blk_update",
                                                 create_weather_agent_service(10000+i, core_name)))
        tasks.append(task)
    for task in tasks:
        await task


async def set_locations(director: Director, city_num: int):
    grid = EnglandGrid.EnglandGrid(city_num)
    grid.load()
    core_names = get_core_names(grid)
    i = 0
    names = director.get_node_names()
    for key, entity in grid.entities.items():
        if entity.kind != "CITY":
            continue
        print("SET LOCATION {} NODE TO {}".format(names[i], entity.name))
        core_name = next(core_names)+"-core"
        await director.set_location(names[i], core_name.encode("UTF-8"), (entity.coords[1], entity.coords[0])) #lon, lat
        i += 1
        if i >= len(names):
            break


async def set_locations_and_connections(director: Director, city_num: int):
    grid = EnglandGrid.EnglandGrid(city_num)
    grid.load()

    core_names = get_core_names(grid)

    peers = {}
    addresses = {}
    for key, entity in grid.entities.items():
        if entity.kind != "CITY":
            continue
        core_name = next(core_names)+"-core"
        a = director.get_address(core_name)
        if len(a) == 0:
            continue
        print("SET LOCATION {}@{}:{} NODE TO {}".format(core_name, a[0], a[1], entity.name))
        addresses[core_name] = a
        peers[core_name] = [link[0].name for link in entity.links if link[1] == "GND"]
        if core_name == "London":
            peers[core_name].append("Birmingham")
        if core_name == "Birmingham":
            peers[core_name].append("London")
        await director.set_location(core_name, core_name.encode("utf-8"), (entity.coords[1], entity.coords[0]))#lon, lat
    for key in peers:
        targets = [("Search"+str(addresses[peer][1]-40000), addresses[peer][0], addresses[peer][1]-20000)
                   for peer in peers[key] if peer in addresses]
        print("ADD PEERS for search {}: ".format(key), targets)
        await director.add_peers(key, targets)


async def config_from_json(director: Director, json_config: str):
    with open(json_config, "r") as f:
        config = json.load(f)
    internal_hosts = config["internal_hosts"]
    config = config["nodes"]
    print(config)

    uri_map = {}

    for c in config:
        host, port = c["director_uri"].split(":")
        name = c["name"]
        await set_node(director, host, port, name)
        coords = c["location"]
        core_name = name+"-core"
        print("SET LOCATION {}@{} NODE TO {}".format(core_name, c["core_uri"], coords))
        await director.set_location(name, core_name.encode("utf-8"), tuple(coords))
        uri_map[name] = c["uri"]

    for c in config:
        peers = [(peer, *uri_map[peer].split(":")) for peer in c["peers"] if peer in uri_map]
        peers = [(d[0]+"-search", d[1] if d[0] not in internal_hosts else internal_hosts[d[0]], d[2]) for d in peers]
        print("ADD PEERS for search {}: ".format(c["name"]), peers)
        await director.add_peers(c["name"], peers)

    await director.reset()

    tasks = []
    for c in config:
        host, port = c["uri"].split(":")
        name = c["name"]
        core_name = name+"-core"
        await set_node(director, host, port, c["name"])
        core_host, core_port = c["core_uri"].split(":")
        print("SET WEATHER AGENT FOR: ", name, "; core_name: ", core_name, "; address: {}:{}".format(core_host, core_port))
        task = asyncio.create_task(director.send(name, "blk_update",
                                                 create_weather_agent_service(int(core_port), core_name, core_host)))
        tasks.append(task)
    for task in tasks:
        await task


async def main(args):
    director = Director()

    if args.targets is not None and len(args.targets) > 0:
        await set_nodes(director, args.targets)

    if args.type == "location":
        await set_locations(director, args.city_num)
    elif args.type == "weather_agent":
        await set_weather_agents(director)
    elif args.type == "location_and_connection":
        await set_locations_and_connections(director, args.city_num)
    elif args.type == "json_config":
        if len(args.config_file) == 0:
            print("json_config requires a json config file!")
            return
        await config_from_json(director, args.config_file)
    else:
        print("Command type {} not supported!".format(args.type))

    await director.close_all()

    await director.wait()


if __name__ == "__main__":
    configure_logging(level=logging.INFO)
    parser = argparse.ArgumentParser(description='DEMO Director')
    parser.add_argument("--targets", nargs='+',  type=str, help="Node addresses host:port ...")
    parser.add_argument("--type", "-t", type=str, required=True, help="weather_agent/location/location_and_connection/json_config")
    parser.add_argument("--config_file", type=str, required=False, default="", help="JSON config file for json_config")
    parser.add_argument("--city_num", type=int, required=False, default=50, help="How many cities?")
    args_ = parser.parse_args()

    asyncio.run(main(args_))

