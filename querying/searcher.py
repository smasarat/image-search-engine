# import the necessary packages
import logging
from logging.config import dictConfig

import numpy as np

from imports_exports.pickle_actions import PickleActions
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
            _pickle_actions = PickleActions(self.indexPath)
            df = _pickle_actions.load_pickle()
            # reader = csv.reader(f)

            # loop over the rows in the index
            for row in df.iterrows():
                # parse out the image ID and features, then compute the
                # chi-squared distance between the features in our index
                # and our query features
                features = list(map(np.float32, row[1]))
                d = self.chi2_distance(features, queryFeatures)

                # now that we have the distance between the two feature
                # vectors, we can udpate the results dictionary -- the
                # key is the current image ID in the index and the
                # value is the distance we just computed, representing
                # how 'similar' the image in the index is to our query
                results[row[0]] = d

            # close the reader
            f.close()

        # try:
        #     df_scores = {}
        #     for image_iter in df.iterrows():
        #         # df.loc[image_iter] = feature_iter[feature_iter][1]
        #         df_scores[image_iter[0]] = self.chi2_distance(df.loc[image_iter[0]], queryFeatures)
        #     print()
        #
        # except Exception as e:
        #     logger.exception(e)

        # sort our results, so that the smaller distances (i.e. the
        # more relevant images are at the front of the list)
        results = sorted(results.items(), key=lambda kv: kv[1])
        print()
        # return our (limited) results
        return results[:limit]


def test_searcher():
    _searcher = Searcher(indexPath="../data/descriptors/description.pkl")
    query_features = [np.random.rand() for i in range(1440)]
    print(_searcher.search(query_features, 10))
