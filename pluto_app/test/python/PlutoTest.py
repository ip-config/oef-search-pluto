import sys
import unittest

from pluto_app.src.python.app import PlutoApp
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2

from dap_api.src.python import DapQuery

def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


class PlutoTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""

        config = {
            "locations": {
                "class": "InMemoryDap",
                "config": {
                    "structure": {
                        "location": {
                            "country": "string"
                        },
                    },
                },
            },
            "data_model_searcher": {
                "class": "SearchEngine",
                "config": {
                    "structure": {
                        "data_model_table": {
                            "data_model_field": "embedding"
                        },
                    },
                },
            },
        }

        self.pluto = PlutoApp.PlutoApp()
        self.pluto.setup(config)

        self.pluto.dapManager.setDataModelEmbedder("data_model_searcher", "data_model_table", "data_model_field")

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

        self.dm1 = dm1
        self.dm2 = dm2
        self.dm3 = dm3

        self.setupAgents()

    def _createUpdate(self, agent_name, fieldname, typename, data):
        update = dap_update_pb2.DapUpdate()
        newvalue = update.update.add()
        f = self.pluto.getField(fieldname)
        newvalue.tablename = f['table']
        newvalue.fieldname = fieldname

        newvalue.value.type = {
            'string': 2,
            'embedding': 7,
            'dm': 6,
        }[typename]
        if typename == "string":
            newvalue.value.s = data
        if typename == "embedding":
            newvalue.value.embedding = data
        if typename == "dm":
            newvalue.value.dm.CopyFrom(data)

        newvalue.key.agent_name = agent_name
        newvalue.key.core_uri.append("localhost:10000")
        return update

    def setupAgents(self):
        for agent_name, fieldname, typename, data in [
            ("007/James/Bond/Weather",      "data_model_field", "dm", self.dm1),
            ("White/Spy/Book",              "data_model_field", "dm", self.dm2),
            ("Black/Spy/BookMoreDataNovel", "data_model_field", "dm", self.dm3),
            ("86/Maxwell/Smart/Weather",    "data_model_field", "dm", self.dm1),

            ("007/James/Bond/Weather",      "country", "string", "UK"),
            ("White/Spy/Book",              "country", "string", "US"),
            ("Black/Spy/BookMoreDataNovel", "country", "string", "UK"),
            ("86/Maxwell/Smart/Weather",    "country", "string", "US"),
        ]:
            print(">>", agent_name, fieldname)
            update = self._createUpdate(agent_name, fieldname, typename, data)
            self.pluto.update(update)

    def testDataModelAndAttributeQuery(self):
        """Test case A. note that all test method names must begin with 'test.'"""

        qm = query_pb2.Query.Model()
        dmq = qm.model

        dmq.name = "sunshine"
        dmq.description = "Give me some weather data"
        dmq.attributes.extend([
            get_attr_b("wind_stuff", "Is windy outside?"),
            get_attr_b("celsius", "Freezing or warm?"),
            get_attr_b("pascal", "Under pressure")
        ])

        qc = qm.constraints.add()

        qc.constraint.attribute_name = "country"
        qc.constraint.relation.op = 0
        qc.constraint.relation.val.s = "UK"

        dapQuery = self.pluto.dapManager.makeQuery(qm)
        dapQuery.print()
        results = list(self.pluto.dapManager.execute(dapQuery))

        print(results)
        assert len(results) == 100

