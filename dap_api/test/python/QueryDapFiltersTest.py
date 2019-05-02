import unittest
import sys

from dap_api.src.python import DapInterface
from dap_api.src.python import DapManager
from dap_api.src.python import DapQueryRepn
from dap_in_memory.src.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_2d_geo.src.python import DapGeo
from ai_search_engine.src.python import SearchEngine
from utils.src.python.Logging import has_logger

def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


def create_dm(name: str, description: str, attributes: list) -> query_pb2.Query.DataModel:
    dm = query_pb2.Query.DataModel()
    dm.name = name
    dm.description = description
    dm.attributes.extend(attributes)
    return dm

class QueryDapFiltersTest(unittest.TestCase):

    @has_logger
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Call before every test case."""
        pass

    def _createUpdate(self, agent_name):
        update = dap_update_pb2.DapUpdate()
        newvalue = update.update.add()
        newvalue.tablename = "not_a_valid_tablename"
        newvalue.fieldname = "not_a_valid_fieldname"
        newvalue.value.type = 2
        newvalue.value.s = "moo"
        newvalue.key.agent = agent_name.encode("utf-8")
        newvalue.key.core = "localhost".encode("utf-8")
        return update

    def testFieldOptionsWork(self):
        dapManager = DapManager.DapManager()
        self.dapManager = dapManager

        dapManagerConfig = {
            "data_model_searcher": {
                "class": "SearchEngine",
                "config": {
                    "structure": {
                        "data_model_table": {
                            "data_model": "embedding"
                        },
                    },
                },
            },
            "geo": {
                "class": "DapGeo",
                "config": {
                    "structure": {
                        "location": {
                            "location": {
                                "type": "location",
                                "options": [
                                    "plane",
                                ]
                            }
                        },
                    },
                },
            },
        }
        dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

        dapManager.setDataModelEmbedder('data_model_searcher', 'data_model_table', 'data_model')

        dm1 = query_pb2.Query.DataModel()
        dm1.name = "weather_data"
        dm1.description = "All possible weather data."
        dm1.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements.",0),
            get_attr_b("temperature", "Provides wind speed measurements.",1),
            get_attr_b("air_pressure", "Provides wind speed measurements.",2)
        ])
        dm2 = query_pb2.Query.DataModel()
        dm2.name = "more weather"
        dm2.description = "More weather"
        dm2.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements.",0),
            get_attr_b("temperature", "Provides wind speed measurements.",1),
            get_attr_b("rain_fall", "Provides wind speed measurements.",2)
        ])
        dm3 = query_pb2.Query.DataModel()
        dm3.name = "book_store_new"
        dm3.description = "Other bookstore"
        dm3.attributes.extend([
            get_attr_b("title", "The title of the book", 1),
            get_attr_b("author", "The author of the book", 3),
            get_attr_b("ISBN", "That code thing", 4),
            get_attr_b("price", "We will need a lot of money", 3),
            get_attr_b("count", "How many do we have", 0),
            get_attr_b("condition", "Our books are in the best condition", 0)
        ])

        engine = dapManager.getInstance('data_model_searcher')
        embed1 = engine._dm_to_vec(dm1)
        embed2 = engine._dm_to_vec(dm2)
        embed3 = engine._dm_to_vec(dm3)

        lat = 0
        lon = 0
        count = 1
        for agent, loc, model in [
            ("007/James/Bond",   (51.477,-0.461), dm1), # LHR, WEATHER
            ("White/Spy",        (53.354,-2.275), dm2), # MANCHESTER, WEATHER
            ("Black/Spy",        (50.734,-3.414), dm3), #EXETER, BOOKSHOP
            ("86/Maxwell/Smart", (40.640,-73.779), dm1), # JFK, WEATHER
        ]:
            update = dap_update_pb2.DapUpdate()
            update.update.add()
            update.update[0].tablename = "location"
            update.update[0].fieldname = "location.update"
            update.update[0].key.core = b'localhost'
            update.update[0].key.agent = agent.encode("utf-8")
            update.update[0].value.l.lat = loc[0]
            update.update[0].value.l.lon = loc[1]
            update.update[0].value.type = 9
            dapManager.update(update)

            update = self._createUpdate(agent)
            update.update.add()
            update.update[0].tablename = "data_model_table"
            update.update[0].fieldname = "data_model"
            update.update[0].value.type = 6
            update.update[0].value.dm.CopyFrom(model)
            self.dapManager.update(update)

        qm = query_pb2.Query.Model()
        qAnd = qm.constraints.add()
        q1 = qAnd.and_.expr.add()

        q1.constraint.attribute_name = "location"
        q1.constraint.relation.op = 0
        q1.constraint.distance.center.lat = 52.454
        q1.constraint.distance.center.lon = -1.748   # BHX
        q1.constraint.distance.distance = 150 * 1000

        qm.model.CopyFrom(create_dm("weather_data",
         "All possible weather data.", [
             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
             get_attr_b("temperature", "Provides wind speed measurements.", 0),
             get_attr_b("air_pressure", "Provides wind speed measurements.", 0)
        ]))

        dapQuery = self.dapManager.makeQuery(qm)
        output = self.dapManager.execute(dapQuery)

        agents = sorted([
            result.agent
            for result
            in output.identifiers
        ])

        self.log.warning("agents={}".format(agents))

        assert(agents == [
            b"007/James/Bond",
            b"White/Spy",
        ])

    def testFieldOptionsWork2(self):
        dapManager = DapManager.DapManager()
        self.dapManager = dapManager

        dapManagerConfig = {
            "data_model_searcher": {
                "class": "SearchEngine",
                "config": {
                    "structure": {
                        "data_model_table": {
                            "data_model": "embedding"
                        },
                    },
                },
            },
            "geo": {
                "class": "DapGeo",
                "config": {
                    "structure": {
                        "location": {
                            "location.location": {
                                "type": "location",
                                "options": [
                                    "plane",
                                ]
                            }
                        },
                    },
                },
            },
        }
        dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)

        dapManager.setDataModelEmbedder('data_model_searcher', 'data_model_table', 'data_model')

        dm1 = query_pb2.Query.DataModel()
        dm1.name = "weather_data"
        dm1.description = "All possible weather data."
        dm1.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements.",0),
            get_attr_b("temperature", "Provides wind speed measurements.",1),
            get_attr_b("air_pressure", "Provides wind speed measurements.",2)
        ])
        dm2 = query_pb2.Query.DataModel()
        dm2.name = "more weather"
        dm2.description = "More weather"
        dm2.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements.",0),
            get_attr_b("temperature", "Provides wind speed measurements.",1),
            get_attr_b("rain_fall", "Provides wind speed measurements.",2)
        ])
        dm3 = query_pb2.Query.DataModel()
        dm3.name = "book_store_new"
        dm3.description = "Other bookstore"
        dm3.attributes.extend([
            get_attr_b("title", "The title of the book", 1),
            get_attr_b("author", "The author of the book", 3),
            get_attr_b("ISBN", "That code thing", 4),
            get_attr_b("price", "We will need a lot of money", 3),
            get_attr_b("count", "How many do we have", 0),
            get_attr_b("condition", "Our books are in the best condition", 0)
        ])

        engine = dapManager.getInstance('data_model_searcher')
        embed1 = engine._dm_to_vec(dm1)
        embed2 = engine._dm_to_vec(dm2)
        embed3 = engine._dm_to_vec(dm3)

        update = dap_update_pb2.DapUpdate()
        update.update.add()
        update.update[0].tablename = "location"
        update.update[0].fieldname = "location.update"
        update.update[0].key.core = b'localhost'
        update.update[0].key.agent = b''
        update.update[0].value.l.lat = 51.477
        update.update[0].value.l.lon = -0.461
        update.update[0].value.type = 9
        dapManager.update(update)

        for agent, _, model in [
            ("007/James/Bond",   (51.477,-0.461), dm1), # LHR, WEATHER
            ("White/Spy",        (53.354,-2.275), dm2), # MANCHESTER, WEATHER
            ("Black/Spy",        (50.734,-3.414), dm3), #EXETER, BOOKSHOP
            ("86/Maxwell/Smart", (40.640,-73.779), dm1), # JFK, WEATHER
        ]:
            update = self._createUpdate(agent)
            update.update[0].fieldname = "data_model"
            update.update[0].tablename = "data_model_table"
            update.update[0].value.type = 6
            update.update[0].value.dm.CopyFrom(model)
            self.dapManager.update(update)

        qm = query_pb2.Query.Model()
        qAnd = qm.constraints.add()
        q1 = qAnd.and_.expr.add()

        q1.constraint.attribute_name = "location"
        q1.constraint.relation.op = 0
        q1.constraint.distance.center.lat = 52.454
        q1.constraint.distance.center.lon = -1.748   # BHX
        q1.constraint.distance.distance = 150 * 1000

        qm.model.CopyFrom(create_dm("weather_data",
         "All possible weather data.", [
             get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
             get_attr_b("temperature", "Provides wind speed measurements.", 0),
             get_attr_b("air_pressure", "Provides wind speed measurements.", 0)
        ]))

        dapQuery = self.dapManager.makeQuery(qm)
        output = self.dapManager.execute(dapQuery)

        agents = sorted([
            result.agent
            for result
            in output.identifiers
        ])

        

        assert(agents == sorted([
            b"007/James/Bond",
            b"86/Maxwell/Smart",
            b"White/Spy",
        ]))

if __name__ == "__main__":
    from utils.src.python.Logging import configure as configure_logging
    configure_logging()
    unittest.main() # run all tests

