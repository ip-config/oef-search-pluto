from api.experimental.python.Director import Director
from utils.src.python.Logging import configure
import asyncio


async def set_nodes(director: Director):
    await director.add_node("127.0.0.1", 40000, "FullNode1")


async def set_locations(director: Director):
    await director.set_location("FullNode1", "1-core".encode("UTF-8"), (4.3, 34.3))


async def main():
    configure()
    director = Director()

    await set_nodes(director)

    await set_locations(director)

    await director.close_all()

    await director.wait()

if __name__ == "__main__":
    asyncio.run(main())
