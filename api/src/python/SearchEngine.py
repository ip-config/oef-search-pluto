from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger
import gensim.downloader
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import numpy as np
import scipy.spatial.distance as distance


class SearchEngine:
    @has_logger
    def __init__(self):
        self._storage = {}
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')
        self._stop_words = set(stopwords.words('english'))
        self._w2v = gensim.downloader.load("glove-wiki-gigaword-50") #"word2vec-google-news-300")
        self._porter = PorterStemmer()
        self._wnl = WordNetLemmatizer()
        self._encoding_dim = 50

    def _string_to_vec(self, description: str):
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
                final.append(w1)
            else:
                final.append(self._porter.stem(w))
        #print("Final: ", final)
        feature_vec = np.zeros((self._encoding_dim,))
        counter = 0
        for w in final:
            try:
                feature_vec = np.add(self._w2v[w], feature_vec)
                counter += 1
            except KeyError as e:
                self.log.warning("Failed to embed word: %s" % w)
        if counter > 0:
            feature_vec = np.divide(feature_vec, float(counter))
        return feature_vec

    def add(self, data: query_pb2.Query.DataModel):
        avg_feature = np.zeros((self._encoding_dim,))
        for attr in data.attributes:
            avg_feature = np.add(avg_feature, self._string_to_vec(attr.description))
            avg_feature = np.add(avg_feature, self._string_to_vec(attr.name))
        avg_feature = np.add(avg_feature, self._string_to_vec(data.name))
        avg_feature = np.add(avg_feature, self._string_to_vec(data.description))
        self._storage[avg_feature.tobytes()] = data
        return avg_feature

    def search(self, query: str) -> str:
        encoded = self._string_to_vec(query)
        response = ""
        for key in self._storage:
            data = self._storage[key]
            score = distance.cosine(np.frombuffer(key), encoded)
            response += str(score) + " -> " + data.name
        return response
