
import gensim
import gensim.downloader
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import numpy as np
import scipy.spatial.distance as distance
import json

from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos.dap_update_pb2 import DapUpdate
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.python.DapInterface import DapInterface
from dap_api.src.python.DapQuery import DapQuery
from dap_api.src.python.DapQueryRepn import DapQueryRepn
from dap_api.src.python.DapQueryResult import DapQueryResult
from dap_api.src.python.SubQueryInterface import SubQueryInterface
from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger
from typing import List
from dap_api.src.python.network.DapNetwork import network_support


class SearchEngine(DapInterface):
    @has_logger
    @network_support
    def __init__(self, name, config):
        self._storage = {}
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')
        self._stop_words = set(stopwords.words('english'))
        self._porter = PorterStemmer()
        self._wnl = WordNetLemmatizer()
        self._encoding_dim = 50

        self.store = {}
        self.name = name
        self.structure_pb = config["structure"]

        host = config["host"]
        port = config["port"]

        self.start_network(self, host, port)

        self.tablenames = []
        self.structure = {}

        # Load lazily if used.
        self._w2v = None

        for table_name, fields in self.structure_pb.items():
            self.tablenames.append(table_name)
            for field_name, field_type in fields.items():
                self.structure.setdefault(table_name, {}).setdefault(field_name, {})['type'] = field_type

    def inject_w2v(self, w2v):
        self._w2v = w2v

    def _string_to_vec(self, description: str):
        if not self._w2v:
            self._w2v = gensim.downloader.load("glove-wiki-gigaword-50") #"word2vec-google-news-300")

        #print("Encode desc: ", description)
        if description.find("_") > -1:
            description = description.replace("_", " ")
        tokens = word_tokenize(description)
        words = [word.lower() for word in tokens if word.isalpha()]
        #print("Words: ", words)
        no_stops = [word for word in words if word not in self._stop_words]
        final = []
        for w in no_stops:
            w1 = self._wnl.lemmatize(w)
            if w1.endswith('e'):
                final.append((w1, w))
            else:
                final.append((self._porter.stem(w), w1))
        #print("Final: ", final)
        feature_vec = np.zeros((self._encoding_dim,))
        counter = 0
        for w in final:
            try:
                feature_vec = np.add(self._w2v[w[0]], feature_vec)
                counter += 1
            except KeyError as e:
                try:
                    feature_vec = np.add(self._w2v[w[1]], feature_vec)
                    counter += 1
                except KeyError as e:
                    print("Key %s not found, ignoring..." % w[1])
        if counter > 1:
            feature_vec = np.divide(feature_vec, float(counter))
        return feature_vec

    def _dm_to_vec(self, data: query_pb2.Query.DataModel):
        avg_feature = np.zeros((self._encoding_dim,))
        counter = 2
        for attr in data.attributes:
            avg_feature = np.add(avg_feature, self._string_to_vec(attr.description))
            avg_feature = np.add(avg_feature, self._string_to_vec(attr.name))
            counter += 2
        avg_feature = np.add(avg_feature, self._string_to_vec(data.name))
        avg_feature = np.add(avg_feature, self._string_to_vec(data.description))
        avg_feature = np.divide(avg_feature, float(counter)) #todo check without, seemed to be good
        return avg_feature

    def describe(self) -> dap_description_pb2.DapDescription:
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        for table_name, fields in self.structure_pb.items():
            result_table = result.table.add()
            result_table.name = table_name
            for field_name, field_type in fields.items():
                result_field = result_table.field.add()
                result_field.name = field_name
                result_field.type = field_type
        return result

    def _get_avg_oef_vec(self, row, vec_field):
        avg_feature = np.zeros((self._encoding_dim,))
        counter = 0
        for f in row:
            if f == vec_field:
                continue
            vec = self._dm_to_vec(row[f])
            if not any(vec):
                self.log.warning("Failed to calculate embedding for dm!")
                print(v)
                raise Exception("Embedding failed")
            avg_feature = np.add(avg_feature,vec)
            counter += 1
        if counter > 1:
            avg_feature = np.divide(avg_feature, float(counter))
        return avg_feature

    def update(self, update_data: DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True
        upd = update_data
        if upd:
            k, v = "dm", upd.value.dm
            tbname = self.tablenames[0]
            if upd.fieldname not in self.structure[tbname]:
                raise DapBadUpdateRow("No such field", tbname, upd.key.core, upd.fieldname, k)

            field_type = self.structure[tbname][upd.fieldname]['type']
            if field_type != 'embedding':
                r.narrative.append(
                    "Bad Type tname={} key={} fname={} ftype={} vtype={}".format(tbname, upd.key, upd.fieldname, ftype,
                                                                                 k))
                r.success = False
            row = self.store.setdefault(tbname, {}).setdefault(upd.key.core, {}).setdefault(upd.key.agent, {})
            row[v.name] = v
            row[upd.fieldname] = self._get_avg_oef_vec(row, upd.fieldname)
        return r

    def blk_update(self, update_data: DapUpdate):
        for upd in update_data.update:
            self.update(upd)

    def remove(self, remove_data: DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True

        upd = remove_data
        if upd:
            k, v = "dm", upd.value.dm
            tbname = self.tablenames[0]
            if upd.fieldname not in self.structure[tbname]:
                r.narrative.append("No such field  key={} fname={}".format(upd.key, upd.fieldname))
                r.success = False
            field_type = self.structure[tbname][upd.fieldname]['type']
            if field_type != 'embedding':
                r.narrative.append("Bad Type tname={} key={} fname={} ftype={} vtype={}".format(tbname, upd.key, upd.fieldname, ftype, k))
                r.success = False
            try:
                row = self.store[tbname][upd.key.core][upd.key.agent]
                success |= row.pop(v.name, None) is not None
                row[upd.fieldname] = self._get_avg_oef_vec(row, upd.fieldname)
                if np.sum(row[upd.fieldname]) == 0:
                    self.store[tbname][upd.key.core].pop(upd.key.agent, None)
            except KeyError:
                pass
        return r

    def removeAll(self, key):
        return self.store[self.tablenames[0]].pop(key, None) is not None

    class SubQuery(SubQueryInterface):
        NAMES = [
            "query_field_type",
            "query_field_value",
            "target_field_type",
            "target_field_name",
            "target_table_name",
        ]

        def __init__(self):
            pass

        def fromLeaf(self, leaf: DapQueryRepn.Leaf):
            if leaf == None:
                return

            if leaf.operator != "CLOSE_TO":
                raise ValueError("{} is not an embed search operator.".format(leaf.operator))
            #if target_field_type != "embedding":
            #    raise ValueError("{}.{}({}) is not something an embed search runs on.". format(
            #        leaf.target_table_name,
            #        leaf.target_field_name,
            #        leaf.target_field_type
            #        )
            #    );

            self.query_field_type  = leaf.query_field_type
            self.query_field_value = leaf.query_field_value
            self.target_field_type = leaf.target_field_type
            self.target_field_name = leaf.target_field_name
            self.target_table_name = leaf.target_table_name

            self.prepare()
            return self

        def prepare(self):
            self.enc_query = np.zeros((self.searchSystem._encoding_dim,))
            if self.query_field_type == "string":
                self.enc_query = np.add(self.enc_query, self.searchSystem._string_to_vec(self.query_field_value))
            elif self.query_field_type == "data_model":
                self.enc_query = np.add(self.enc_query, self.searchSystem._dm_to_vec(self.query_field_value))
            return self

        def setSearchSystem(self, searchSystem):
            self.searchSystem = searchSystem
            return self

        def execute(self, key_selector: List[DapQueryResult] = None):
            if key_selector == []:
                return []

            key_list = []
            if key_selector is None:
                key_list = []
                for core in self.searchSystem.store[self.target_table_name].keys():
                    agents = self.searchSystem.store[self.target_table_name][core].keys()
                    if len(agents) > 0:
                        for agent in agents:
                            key_list.append((core, agent))
                    else:
                        key_list.append(core)
            else:
                for key in key_selector:
                    key_list.append(key(True))
            result = []
            for key in key_list:
                data = self.searchSystem.store[self.target_table_name][key[0]][key[1]]
                dist = distance.cosine(data[self.target_field_name], self.enc_query)
                result.append((*key, dist))
            ordered = sorted(result, key=lambda x: x[2])
            res = DapQueryResult(ordered[0][0], ordered[0][1])
            res.score = ordered[0][2]
            yield res
            for i in range(1, len(ordered)):
                if ordered[i][2] < 0.2:
                    res = DapQueryResult(ordered[i][0], ordered[i][1])
                    res.score = ordered[i][2]
                    yield res

        def toJSON(self):
            r = {}
            for k in SearchEngine.SubQuery.NAMES:
                r[k] = getattr(self, k)
            return json.dumps(r)

        def fromJSON(self, data):
            r = json.loads(data)
            for k in SearchEngine.SubQuery.NAMES:
                setattr(self, k, r.get(k, None))
            return self

    def execute(self, proto:  dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        graphQuery = SearchEngine.SubQuery().setSearchSystem(self).fromJSON(query_memento.memento.decode("utf-8")).prepare()

        if input_idents.HasField('originator') and input_idents.originator:
            idents = None
        else:
            idents = [ DapQueryResult(x) for x in input_idents.identifiers ]
        reply = dap_interface_pb2.IdentifierSequence()
        reply.originator = False
        for core in graphQuery.execute(idents):
            c = reply.identifiers.add()
            c.core = core()
        return reply

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        q = SearchEngine.SubQuery().setSearchSystem(self).fromLeaf(DapQueryRepn.Leaf().fromProto(proto))
        r = dap_interface_pb2.ConstructQueryMementoResponse()
        r.memento = q.toJSON().encode('utf8')
        return r

    def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.Branch) -> SubQueryInterface:
        return None
