import json
from england_grid.src.python.lib import EnglandGrid
import argparse


def city_iter(grid):
    grid_it = iter(grid.entities.items())

    while True:
        try:
            key, entity = next(grid_it)
            if entity.kind == "CITY":
                yield entity
        except StopIteration:
            break
    raise StopIteration()


def main(num: int, file: str):
    grid = EnglandGrid.EnglandGrid(num)
    grid.load()
    city_it = city_iter(grid)

    CORE_PORT = 10000
    SEARCH_PORT = 20000
    DIRECTOR_PORT = 40000

    config = {"nodes": [], "internal_hosts": {}}

    nodes = config["nodes"]
    internal_hosts = config["internal_hosts"]
    for i in range(num):
        entity = next(city_it)
        #EXTERNAL INFO
        entry = {
            "uri": "127.0.0.1:{}".format(SEARCH_PORT+i),
            "core_uri": "127.0.0.1:{}".format(CORE_PORT+i),
            "director_uri": "127.0.0.1:{}".format(DIRECTOR_PORT+i),
            "name": entity.name,
            "location": (entity.coords[1], entity.coords[0]), #lon, lat
            "peers": [link[0].name for link in entity.links if link[1] == "GND"]
        }
        nodes.append(entry)
        # inside the container network we have domains for each container instead of 127.0.0.1
        internal_hosts[entity.name] = entity.name + "-container"
    with open(file, "w") as f:
        json.dump(config, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Config file creator')
    parser.add_argument("--file", "-f", type=str, required=True, default="", help="JSON config file for json_config")
    parser.add_argument("--nodes", '-n', type=int, required=True, default=50, help="How many cities?")
    args = parser.parse_args()

    main(args.nodes, args.file)
