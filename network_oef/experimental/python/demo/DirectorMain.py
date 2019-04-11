from api.experimental.python.Director import Director
import argparse
from typing import List
import asyncio
from api.experimental.python.DemoWeatherAgent import create_blk_update as create_weather_agent_service
from england_grid.src.python.lib import EnglandGrid
import sys
import socket
import time


async def set_nodes(director: Director, addresses: List[str]):
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
        await director.add_node(host, port, address)


async def set_weather_agents(director: Director):
    names = director.get_node_names()
    for name in names:
        host, port = name.split(":")
        if host.find("oef_node") != -1:
            i = int(host.replace("oef_node", ""))
        else:
            i = int(port)-20000
        await director.send(name, "blk_update", create_weather_agent_service(10000+i, "Core{}".format(i)))


async def set_locations(director: Director):
    grid = EnglandGrid.EnglandGrid()
    grid.load()

    i = 0
    names = director.get_node_names()
    for key, entity in grid.entities.items():
        core_name = names[i].replace("oef_node", "Core").encode("UTF-8")
        await director.set_location(names[i], core_name, (entity.coords[1], entity.coords[0])) #lon, lat
        i += 1
        if i >= len(names):
            break


async def main(args):
    director = Director()

    await set_nodes(director, args.targets)

    if args.type == "location":
        await set_locations(director)
    elif args.type == "weather_agent":
        await set_weather_agents(director)
    else:
        print("Command type {} not supported!".format(args.type))

    await director.close_all()

    await director.wait()


if __name__ == "__main__":
    print("DIRECTOR GOT ARGS: ", sys.argv)
    parser = argparse.ArgumentParser(description='DEMO Director')
    parser.add_argument("--targets", nargs='+',  type=str, help="Node addresses host:port ...")
    parser.add_argument("--type", type=str, required=True, help="weather_agent/location")
    args_ = parser.parse_args()

    asyncio.run(main(args_))

