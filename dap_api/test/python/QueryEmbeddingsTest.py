import unittest
import sys

from ai_search_engine.src.python import SearchEngine
from dap_in_memory.src.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from dap_api.src.python import DapManager


def get_attr_b(name, desc, type=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = type#query_pb2.Query.Attribute.Type.BOOL
    attr1.required = True
    attr1.description = desc
    return attr1

class QueryEmbeddingsTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.dapManager = DapManager.DapManager()

        dapManagerConfig = {
            "data_model_searcher": {
                "class": "SearchEngine",
                "config": {
                    "structure": {
                        "data_model_table": {
                            "service": "data_model"
                        },
                    },
                },
            },
        }
        self.dapManager.setup(
            sys.modules[__name__],
            dapManagerConfig)
        self.dapManager.setDataModelEmbedder('data_model_searcher', 'data_model_table', 'service')

    def tearDown(self):
        """Call after every test case."""
        pass

    def _createUpdate(self):
        update = dap_update_pb2.DapUpdate()
        newvalue = update.update.add()
        newvalue.tablename = "wibbles"
        newvalue.fieldname = "wibble"
        newvalue.value.type = 2
        newvalue.value.s = "moo"
        newvalue.key.agent = b"007/James/Bond"
        newvalue.key.core = b"localhost:10000"
        return update

    def _createQueryProto(self):
        q = py_oef_protocol_pb2.ConstraintExpr()

    def _setupAgents(self):
        #for agent_name, wibble_value in [
        #    (b"007/James/Bond", "apple"),
        #    (b"White/Spy", "banana"),
        #    (b"Black/Spy", "carrot"),
        #    (b"86/Maxwell/Smart", "carrot"),
        #]:
        #    update = self._createUpdate()
        #    update.update[0].key.agent = agent_name
        #    update.update[0].value.s = wibble_value
        #    self.dapManager.update(update)

        dm1 = query_pb2.Query.DataModel()
        dm1.name = "weather_data"
        dm1.description = "All possible weather data."
        dm1.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements.",0),
            get_attr_b("temperature", "Provides wind speed measurements.",1),
            get_attr_b("air_pressure", "Provides wind speed measurements.",2)
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
        dm3.description = "Other bookstore"
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
        engine = SearchEngine.SearchEngine('temporary', {
            "structure": {
                "data_model_table": {
                    "data_model": "data_model"
                    },
                },
            })

        embed1 = engine._dm_to_vec(dm1)
        embed2 = engine._dm_to_vec(dm2)
        embed3 = engine._dm_to_vec(dm3)


        dmq = query_pb2.Query.DataModel()
        dmq.name = "sunshine"
        dmq.description = "Give me some weather data"
        dmq.attributes.extend([
            get_attr_b("wind_stuff", "Is windy outside?"),
            get_attr_b("celsius", "Freezing or warm?"),
            get_attr_b("pascal", "Under pressure")
        ])

        self.embed3 = engine._dm_to_vec(dmq)

        dmq2 = query_pb2.Query.DataModel()
        dmq2.name = "novels"
        dmq2.description = "I want to read novels"
        dmq2.attributes.extend([
            get_attr_b("name", "Novel has a name"),
            get_attr_b("writer", "Somebody has written the pages"),
        ])
        self.embed4 = engine._dm_to_vec(dmq2)

        print("======================================QUERY WEATHER======================================")
        print(dmq)
        print("======================================QUERY BOOK======================================")
        print(dmq2)

        for agent_name, wibble_value in [
            (b"007/James/Bond", dm1),
            (b"White/Spy", dm1),
            (b"Black/Spy", dm2),
            (b"86/Maxwell/Smart", dm3),
        ]:
            update = self._createUpdate()
            update.update[0].fieldname = "service"
            update.update[0].tablename = "service"
            update.update[0].value.type = 6
            update.update[0].key.agent = agent_name
            update.update[0].value.dm.CopyFrom(wibble_value)
            self.dapManager.update(update)



    def testQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self._setupAgents()

        q = query_pb2.Query.ConstraintExpr()

        q.constraint.attribute_name = "service"
        q.constraint.relation.op = 0
        q.constraint.embedding.val.v.extend(self.embed3)

        dapQuery1 = self.dapManager.makeQueryFromConstraint(q)
        results = list(self.dapManager.execute(dapQuery1))

        q2 = query_pb2.Query.ConstraintExpr()

        q2.constraint.attribute_name = "service"
        q2.constraint.relation.op = 0
        q2.constraint.embedding.val.v.extend(self.embed4)

        dapQuery2 = self.dapManager.makeQuery(q2)
        results2 = list(self.dapManager.execute(dapQuery2))

        print("Looking for weather")
        print(results)
        print("Looking for book")
        print(results2)
        assert len(results) == 2
        assert len(results2) == 2
    #
    # def testQueryOr(self):
    #     """Test case A. note that all test method names must begin with 'test.'"""
    #     self._setupAgents()
    #
    #     qOr = query_pb2.Query.ConstraintExpr()
    #     q1 = qOr.or_.expr.add()
    #     q2 = qOr.or_.expr.add()
    #
    #     q1.constraint.attribute_name = "wibble"
    #     q1.constraint.relation.op = 0
    #     q1.constraint.relation.val.s = "carrot"
    #
    #     q2.constraint.attribute_name = "wibble"
    #     q2.constraint.relation.op = 0
    #     q2.constraint.relation.val.s = "apple"
    #
    #
    #     dapQuery = self.dap1.makeQuery(qOr, "wibbles")
    #     results = list(self.dap1.query(dapQuery))
    #
    #     print(results)
    #     assert len(results) == 3
