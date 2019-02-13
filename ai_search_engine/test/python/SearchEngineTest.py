import unittest

from ai_search_engine.src.python.SearchEngine import SearchEngine
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python.DapQuery import DapQuery
from dap_api.src.python import DapQueryRepn


def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


class SearchEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.se = SearchEngine("search_engine", {"structure": {"dm_store": {"data_model": "embedding"}}})
        cls._setupAgents()

    def setUp(self):
        """Call before every test case."""
        self.se.blk_update(self.update)

    def tearDown(self):
        """Call after every test case."""
        pass

    @classmethod
    def _addUpdate(cls, update: dap_update_pb2.DapUpdate, agent_name: str, data_model: query_pb2.Query.DataModel):
        newvalue = update.update.add()
        newvalue.tablename = "dm_store"
        newvalue.fieldname = "data_model"
        newvalue.value.type = 6
        newvalue.value.dm.name = data_model.name
        newvalue.value.dm.description = data_model.description
        newvalue.value.dm.attributes.extend(data_model.attributes)
        newvalue.key = agent_name.encode("utf-8")
        return update

    @classmethod
    def _setupAgents(cls):
        dm1 = query_pb2.Query.DataModel()
        dm1.name = "weather_data"
        dm1.description = "All possible weather data."
        dm1.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements.", 0),
            get_attr_b("temperature", "Provides wind speed measurements.", 1),
            get_attr_b("air_pressure", "Provides wind speed measurements.", 2)
        ])
        dm2 = query_pb2.Query.DataModel()
        dm2.name = "book_data"
        dm2.description = "Book store data"
        dm2.attributes.extend([
            get_attr_b("title", "The title of the book", 1),
            get_attr_b("author", "The author of the book", 3),
            get_attr_b("release_year", "Release year of the book in the UK",4),
            get_attr_b("introduction", "Short introduction by the author.",3),
            get_attr_b("rating", "Summary rating of the book given by us.",0)
        ])
        dm3 = query_pb2.Query.DataModel()
        dm3.name = "book_store_new"
        dm3.description = "Other bookstore. Focuses on novels."
        dm3.attributes.extend([
            get_attr_b("title", "The title of the book", 1),
            get_attr_b("author", "The author of the book", 3),
            get_attr_b("ISBN", "That code thing", 4),
            get_attr_b("price", "We will need a lot of money", 3),
            get_attr_b("count", "How many do we have", 0),
            get_attr_b("condition", "Our books are in the best condition", 0)
        ])

        print("======================================WEATHER STATION======================================")
        print(dm1)
        print("======================================BOOK STORE======================================")
        print(dm2)
        print("======================================OTHER BOOK STORE======================================")
        print(dm3)

        update = dap_update_pb2.DapUpdate()
        for agent_name, dm in [
            ("007/James/Bond/Weather", dm1),
            ("White/Spy/Book", dm2),
            ("Black/Spy/BookMoreDataNovel", dm3),
            ("86/Maxwell/Smart/Weather", dm1),
        ]:
            cls._addUpdate(update, agent_name, dm)
        cls.update = update

    def testDataModelQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm1 = query_pb2.Query.Model()
        dmq1 = qm1.model
        dmq1.name = "sunshine"
        dmq1.description = "Give me some weather data"
        dmq1.attributes.extend([
            get_attr_b("wind_stuff", "Is windy outside?"),
            get_attr_b("celsius", "Freezing or warm?"),
            get_attr_b("pascal", "Under pressure")
        ])

        qm2 = query_pb2.Query.Model()
        dmq2 = qm2.model
        dmq2.name = "novels"
        dmq2.description = "I want to read novels"
        dmq2.attributes.extend([
            get_attr_b("name", "Novel has a name"),
            get_attr_b("writer", "Somebody has written the pages"),
        ])

        print("======================================QUERY WEATHER======================================")
        print(dmq1)
        print("======================================QUERY BOOK======================================")
        print(dmq2)

        query_wrapper =  DapQueryRepn.DapQueryRepn.Leaf(
            operator="CLOSE_TO",
            query_field_value=dmq1,
            query_field_type="data_model",
            target_field_name="data_model",
            target_table_name="dm_store",
        )
        query = self.se.constructQueryConstraintObject(query_wrapper)

        results1 = list(query.execute())

        query_wrapper.query_field_value = dmq2
        query = self.se.constructQueryConstraintObject(query_wrapper)
        results2 = list(query.execute())

        print("Looking for weather")
        print(results1)
        print("Looking for book")
        print(results2)
        assert len(results1) == 2
        assert len(results2) == 2

    def testStringQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        sq1 = "I'm looking for weather data. Sunshine or rain? Would be nice to know about" \
              " wind speed, temperature in celsius and pressure."
        sq2 = "I want to read novels. All novels has a name, and somebody who wrote it!"
        print("======================================QUERY WEATHER======================================")
        print(sq1)
        print("======================================QUERY NOVEL======================================")
        print(sq2)

        query_wrapper = DapQueryRepn.DapQueryRepn.Leaf(
            operator="CLOSE_TO",
            query_field_value=sq1,
            query_field_type="string",
            target_field_name="data_model",
            target_table_name="dm_store",
        )
        query = self.se.constructQueryConstraintObject(query_wrapper)
        results1 = list(query.execute())

        query_wrapper.query_field_value = sq2
        query = self.se.constructQueryConstraintObject(query_wrapper)
        results2 = list(query.execute())

        print("Looking for weather")
        print("Looking for book")
        assert len(results1) == 2
        assert len(results2) == 2
