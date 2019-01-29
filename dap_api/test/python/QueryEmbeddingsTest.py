import unittest

from api.src.python import SearchEngine
from dap_api.src.python import DapInterface
from dap_api.experimental.python import InMemoryDap
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2


def get_attr_b(name, desc):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = 2#query_pb2.Query.Attribute.Type.BOOL
    attr1.required = True
    attr1.description = desc
    return attr1

class QueryEmbeddingsTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.dap1 = InMemoryDap.InMemoryDap("dap1", { "wibbles": { "wibble": "string", "service": "embedding"} } );

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
        newvalue.key.agent_name = "007/James/Bond"
        newvalue.key.core_uri.append("localhost:10000")
        return update

    def _createQueryProto(self):
        q = py_oef_protocol_pb2.ConstraintExpr()

    def _setupAgents(self):
        for agent_name, wibble_value in [
            ("007/James/Bond", "apple"),
            ("White/Spy", "banana"),
            ("Black/Spy", "carrot"),
            ("86/Maxwell/Smart", "carrot"),
        ]:
            update = self._createUpdate()
            update.update[0].key.agent_name = agent_name
            update.update[0].value.s = wibble_value
            self.dap1.update(update)

        dm1 = query_pb2.Query.DataModel()
        dm1.name = "weather_data"
        dm1.description = "All possible weather data."
        dm1.attributes.extend([
            get_attr_b("wind_speed", "Provides wind speed measurements."),
            get_attr_b("temperature", "Provides wind speed measurements."),
            get_attr_b("air_pressure", "Provides wind speed measurements.")
        ])
        dm2 = query_pb2.Query.DataModel()
        dm2.name = "book_data"
        dm2.description = "Book store data"
        dm2.attributes.extend([
            get_attr_b("title", "The title of the book"),
            get_attr_b("author", "The author of the book"),
            get_attr_b("release_year", "Release year of the book in the UK"),
            get_attr_b("introduction", "Short introduction by the author."),
            get_attr_b("rating", "Summary rating of the book given by us.")
        ])
        print("======================================WEATHER STATION======================================")
        print(dm1)
        print("======================================BOOK STORE======================================")
        print(dm2)
        engine = SearchEngine.SearchEngine()

        embed1 = engine.add(dm1)
        embed2 = engine.add(dm2)

        dmq = query_pb2.Query.DataModel()
        dmq.name = "sunshine"
        dmq.description = "Give me some weather data"
        dmq.attributes.extend([
            get_attr_b("wind_stuff", "Is windy outside?"),
            get_attr_b("celsius", "Freezing or warm?"),
            get_attr_b("pascal", "Under pressure")
        ])

        self.embed3 = engine.add(dmq)

        dmq2 = query_pb2.Query.DataModel()
        dmq2.name = "novels"
        dmq2.description = "I want to read novels"
        dmq2.attributes.extend([
            get_attr_b("name", "Novel has a name"),
            get_attr_b("writer", "Somebody has written the book"),
        ])
        self.embed4 = engine.add(dmq2)

        print("======================================QUERY WEATHER======================================")
        print(dmq)
        print("======================================QUERY BOOK======================================")
        print(dmq2)

        for agent_name, wibble_value in [
            ("007/James/Bond", embed1),
            ("White/Spy", embed1),
            ("Black/Spy", embed2),
            ("86/Maxwell/Smart", embed2),
        ]:
            update = self._createUpdate()
            update.update[0].fieldname = "service"
            update.update[0].value.type = 6
            update.update[0].key.agent_name = agent_name
            update.update[0].value.embedding.v.extend(wibble_value)
            self.dap1.update(update)



    def testQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        self._setupAgents()

        q = query_pb2.Query.ConstraintExpr()

        q.constraint.attribute_name = "service"
        q.constraint.relation.op = 0
        q.constraint.embedding.val.v.extend(self.embed3)

        dapQuery = self.dap1.makeQuery(q, "wibbles")
        results = list(self.dap1.query(dapQuery))

        q2 = query_pb2.Query.ConstraintExpr()

        q2.constraint.attribute_name = "service"
        q2.constraint.relation.op = 0
        q2.constraint.embedding.val.v.extend(self.embed4)

        dapQuery2 = self.dap1.makeQuery(q2, "wibbles")
        results2 = list(self.dap1.query(dapQuery2))

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
