from network_oef.experimental.python.FullNodeClass import FullNode
from england_grid.src.python.lib import EnglandGrid
from api.experimental.python.Director import Director
from api.experimental.python.DemoWeatherAgent import create_blk_update as create_weather_agent_service
from utils.src.python.resources import binaryfile
import asyncio
import time


class SearchNetwork:
    def __init__(self):
        self.nodes = {}
        self._addresses = {}
        self._grid = EnglandGrid.EnglandGrid()
        self._grid.load()
        self._cities_it = iter(self._grid.entities.items())
        self._director = Director()
        self._director_weather_service = Director()
        #print(binaryfile("fetch_teams/OEFNode", as_file=True).name)
        self._oef_core = "fetch_teams/OEFNode"#, as_file=True).name

    async def set_location(self, ip: str, port: int, core_key: str, node_key: str):
        await self._director.add_node(ip, port, node_key)
        key, entity = next(self._cities_it)
        await self._director.set_location(node_key, core_key.encode("utf-8"), (entity.coords[1], entity.coords[0]))
        await self._director.close_all()
        await self._director.wait()

    async def set_weather_service(self, ip: str, port: int, node_key: str, core_port: int, core_key: str):
        await self._director_weather_service.add_node(ip, port, node_key)
        await self._director_weather_service.send(node_key, "blk_update", create_weather_agent_service(core_port, core_key))
        await self._director_weather_service.close_all()
        await self._director_weather_service.wait()

    def create_node(self, node_key: str, ip: str, port: int, dap_port: int, director_port: int,  core_key: str = "",
                    core_port: int = -1, http_port: int = -1, ssl_certificate: str = ""):

        print("---------- CREATE NODE: ", node_key)
        node = FullNode()
        node.start_search(node_key, ip, port, dap_port, director_port, http_port, ssl_certificate)
        if len(core_key) > 0 and core_port > 1000:
            node.start_core(core_key, ip, core_port, self._oef_core)
        self._addresses[node_key] = (ip, port)
        self.nodes[node_key] = node
        asyncio.run(self.set_location(ip, director_port, core_key, node_key))
        asyncio.run(self.set_weather_service(ip, port, node_key, core_port, core_key))

    def link(self, node1_key: str, node2_key: str):
        ip1, port1 = self._addresses[node1_key]
        ip2, port2 = self._addresses[node2_key]
        success = self.nodes[node1_key].add_peer(node2_key, ip2, port2)
        success &= self.nodes[node2_key].add_peer(node1_key, ip1, port1)
        return success
