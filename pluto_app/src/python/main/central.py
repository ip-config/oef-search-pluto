#!/usr/bin/env python3
from utils.src.python.Logging import configure as configure_logging
import argparse
from pluto_app.src.python.app import SearchNetwork
from api.src.python.CommunicationHandler import socket_server, http_server, CommunicationHandler
from fake_oef.src.python.lib import ConnectionFactory
from fake_oef.src.python.lib import FakeAgent
from api.src.proto import update_pb2
from fetch_teams.oef_core_protocol import query_pb2


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
    upd.data_models.extend([dm])
    return upd


def create_weather_dm_update(oef) -> update_pb2.Update.BulkUpdate:
    upd1 = create_update(oef,
                         "weather_data",
                         "All possible weather data.", [
                             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
                             get_attr_b("temperature", "Provides wind speed measurements.", 1),
                             get_attr_b("air_pressure", "Provides wind speed measurements.", 2)
                         ])
    return upd1


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--ssl_certificate", required=True, type=str, help="specify an SSL certificate PEM file.")
    parser.add_argument("--http_port", required=True, type=int, help="which port to run the HTTP interface on.")
    parser.add_argument("--socket_port", required=True, type=int, help="which port to run the socket interface on.")
    parser.add_argument("--html_dir", required=False, type=str, help="where ", default="api/src/resources/website")
    args = parser.parse_args()

    connection_factory = ConnectionFactory.ConnectionFactory()

    com = CommunicationHandler(1)
    com.add(http_server, "0.0.0.0", args.http_port, args.ssl_certificate, args.html_dir)

    search_network = SearchNetwork.SearchNetwork({'search-0': com}, [
        'search-0', 'search-1', 'search-2', 'search-3', 'search-4'
        ], connection_factory)

    # Search connectivity
    search_network.set_connection('search-0', ['search-1', 'search-4'])
    search_network.set_connection('search-1', ['search-2', 'search-3'])
    search_network.set_connection('search-2', ['search-3', 'search-4'])
    search_network.set_connection('search-3', ['search-4', 'search-0'])
    search_network.set_connection('search-4', ['srch-1', 'search-2'])

    oef1 = search_network.create_oef_core_for_node("search-3", "oef3")
    oef2 = search_network.create_oef_core_for_node("search-1", "oef1")

    agent1 = FakeAgent.FakeAgent(connection_factory=connection_factory, id='a0')
    agent1.connect(target="oef3")
    agent1.register_service(create_weather_dm_update("oef3"))

    agent2 = FakeAgent.FakeAgent(connection_factory=connection_factory, id='a1')
    agent2.connect(target="oef1")
    agent2.register_service(create_weather_dm_update("oef1"))

    com.wait()




