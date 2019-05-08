import atexit
import logging
import os
import threading
from logging.config import dictConfig
import cv2
import numpy as np
from flask import Flask, jsonify, request

from key_constants import constants
from logs.log_config import LOGGING
from querying.searcher import Searcher
from response_format.response import ResponseFormat
from training.descriptor import ColorDescriptor
from training.fetch_features import AlwaysRunningDfInMemory
from training.train_loop import AlwaysRunningEsIndex
import training.globals as training_globals

dictConfig(LOGGING)
file_logger = logging.getLogger("file")
similar_photos_logger = logging.getLogger("similar_photos_logger")
dataLock = threading.Lock()


# todo: set strategy for determine number of features in config file
# todo: check the possibility of working with different versions of Elasticsearch (7.0)
# todo: rename file_names to short format. (not complete address)
# todo: performance checking of data-frame load.
# todo: check the accuracy of system. whether it returns same as previous results.
# todo: handle the true response especially when dataframe or es are not completely computed.


def create_app():
    app = Flask(__name__)

    def interrupt_es():
        global updating_thread_es
        updating_thread_es.cancel()

    def interrupt_df():
        global updating_thread_df
        updating_thread_df.cancel()

    def do_df_update():
        global updating_thread_df
        # Do your stuff with commonDataStruct Here
        with dataLock:
            _always_running_class = AlwaysRunningDfInMemory()
            _always_running_class.run()
        # Set the next thread to happen
        updating_thread_df = threading.Timer(constants.RE_FETCH_INTERVAL_SEC, do_df_update)
        updating_thread_df.start()

    def do_es_update():
        global updating_thread_es
        # Do your stuff with commonDataStruct Here
        with dataLock:
            _always_running_es_index_class = AlwaysRunningEsIndex()
            _always_running_es_index_class.run()
        # Set the next thread to happen
        updating_thread_es = threading.Timer(constants.RE_INDEX_INTERVAL_SEC, do_es_update)
        updating_thread_es.start()

    def do_es_index_start():
        # Do initialisation stuff here
        global updating_thread_es
        # Create your thread
        updating_thread_es = threading.Timer(constants.RE_INDEX_INTERVAL_SEC, do_es_update)
        updating_thread_es.start()

    def do_df_inmemroy_start():
        # Do initialisation stuff here
        global updating_thread_df
        # Create your thread
        updating_thread_df = threading.Timer(constants.RE_FETCH_INTERVAL_SEC, do_df_update)
        updating_thread_df.start()

    # Initiate
    do_df_inmemroy_start()
    do_es_index_start()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt_es)
    atexit.register(interrupt_df)
    return app


app = create_app()


@app.route('/upload', methods=['POST'])
def get_similar_images():
    file = request.files['file']

    npimg = np.fromstring(file.read(), np.uint8)
    # convert numpy array to image
    query = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    cd = ColorDescriptor(constants.COLOR_DESCRIPTOR_TUPLE)
    features = cd.describe(query)

    # perform the search
    searcher = Searcher(indexPath=constants.TMP_FILE_TO_STORE_DESCRIPTIONS)
    results = searcher.search(features)
    similar_photos = list(map(lambda x: x[1], results))

    file.stream.seek(0)
    file_name = file.filename
    file.save(os.path.join(constants.USER_UPLOAD_DIR, file_name))
    similar_photos_logger.info("uploaded_photo:{}, recommended_photos:{}".format(file_name, similar_photos))

    if constants.SAVE_WHOLE_VALIDATION_SET:
        num = 0
        for (score, result_path) in results:
            num += 1
            # load the result image and display it
            result = cv2.imread(result_path)
            cv2.imwrite(constants.USER_UPLOAD_DIR + str(num) + str(file_name), img=result)

    return jsonify({"resp": "Hello World"})


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    _response_format = ResponseFormat(ids=[], count=0, message="works well!", error_code=0)
    file_logger.info("works well!")
    return jsonify(_response_format.__dict__)


@app.route('/getlastupdatetime')
def get_last_update_time():
    _response_format = ResponseFormat(ids=[training_globals.last_updatetime], count=0, message="works well!", error_code=0)
    file_logger.info("getupdatetime called ! ")
    return jsonify(_response_format.__dict__)
