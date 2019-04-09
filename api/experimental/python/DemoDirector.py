from api.experimental.python.Director import Director
from utils.src.python.Logging import configure
import asyncio
import argparse
from england_grid.src.python.lib import EnglandGrid


async def set_nodes(director: Director, port_start: int, port_end: int):
    num = port_end-port_start+1
    for i in range(num):
        await director.add_node("127.0.0.1", port_start+i, str(i))


async def set_locations(director: Director):
    grid = EnglandGrid.EnglandGrid()
    grid.load()

    i = 0
    names = director.get_node_names()
    for key, entity in grid.entities.items():
        core_name = (entity.name + "-core").encode("UTF-8")
        await director.set_location(names[i], core_name, (entity.coords[1], entity.coords[0])) #lon, lat
        i += 1
        if i >= len(names):
            break


async def main(args):
    configure()
    director = Director()

    await set_nodes(director, args.port_start, args.port_end)

    await set_locations(director)

    await director.close_all()

    await director.wait()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--port_start", required=True, type=int)
    parser.add_argument("--port_end", required=True, type=int)
    asyncio.run(main(parser.parse_args()))
