# import the necessary packages
import logging
import pandas as pd
import numpy as np
import csv

from elasticsearch import Elasticsearch

from key_constants import constants
from logging.config import dictConfig
from logs.log_config import LOGGING

dictConfig(LOGGING)
logger = logging.getLogger("file")


class Searcher:
    def __init__(self, indexPath):
        # store our index path
        self.indexPath = indexPath

    def chi2_distance(self, histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)])

        # return the chi-squared distance
        return d

    def search(self, queryFeatures, limit=10):
        # initialize our dictionary of results
        results = {}
        # open the index file for reading
        with open(self.indexPath) as f:
            # initialize the CSV reader
            reader = csv.reader(f)

            # loop over the rows in the index
            for row in reader:
                # parse out the image ID and features, then compute the
                # chi-squared distance between the features in our index
                # and our query features
                features = [float(x) for x in row[1:]]
                d = self.chi2_distance(features, queryFeatures)

                # now that we have the distance between the two feature
                # vectors, we can udpate the results dictionary -- the
                # key is the current image ID in the index and the
                # value is the distance we just computed, representing
                # how 'similar' the image in the index is to our query
                results[row[0]] = d

            # close the reader
            f.close()

        try:
            es = Elasticsearch(hosts=[{"host": constants.ES_HOST, "port": constants.ES_PORT}])
            query = {"size": 10000, "query": {"match_all": {}}}
            _search_res = es.search(index="image_recommender", body=query)
            n_records = _search_res["hits"]["total"]
            n_features = len(_search_res["hits"]["hits"][0]["_source"]["features"]) if n_records != 0 else 0
            df = pd.DataFrame(columns=list(map(lambda x: "f_" + x, list(map(str, list(range(n_features)))))))

            for hits_iter in _search_res["hits"]["hits"]:
                df.loc[hits_iter["_id"]] = hits_iter["_source"]["features"]



        except Exception as e:
            logger.exception(e)

        # sort our results, so that the smaller distances (i.e. the
        # more relevant images are at the front of the list)
        results = sorted([(v, k) for (k, v) in results.items()])

        # return our (limited) results
        return results[:limit]
