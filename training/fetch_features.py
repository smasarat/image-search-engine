# import the necessary packages
import argparse
import logging
import threading
from logging.config import dictConfig

import pandas as pd

from key_constants import constants
from logs.log_config import LOGGING
from training.globals import set_df

dictConfig(LOGGING)
logger = logging.getLogger("file")
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()


class AlwaysRunningDfInMemory(threading.Thread):
    def stop(self):
        self._running = False

    def run(self):
        try:
            es = Elasticsearch(hosts=[{"host": constants.ES_HOST, "port": constants.ES_PORT}])
            query = {"size": 10000, "query": {"match_all": {}}}
            _search_res = es.search(index="image_recommender", body=query)
            n_records = _search_res["hits"]["total"]
            n_features = len(_search_res["hits"]["hits"][0]["_source"]["features"]) if n_records != 0 else 0
            df = pd.DataFrame(columns=list(map(lambda x: "f_" + x, list(map(str, list(range(n_features)))))))

            for hits_iter in _search_res["hits"]["hits"]:
                df.loc[hits_iter["_id"]] = hits_iter["_source"]["features"]

            set_df(df_=df)

            logger.info("in-memory similarities just created now!")
            # initialize the color descriptor
        except Exception as e:
            logger.exception(e)
