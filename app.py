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
from training.train_loop import AlwaysRunningClass

dictConfig(LOGGING)
file_logger = logging.getLogger("file")
similar_photos_logger = logging.getLogger("similar_photos_logger")
dataLock = threading.Lock()


def create_app():
    app = Flask(__name__)

    def interrupt():
        global updating_thread
        updating_thread.cancel()

    def do_update():
        global updating_thread
        # Do your stuff with commonDataStruct Here
        with dataLock:
            _always_running_class = AlwaysRunningClass()
            _always_running_class.run()
        # Set the next thread to happen
        updating_thread = threading.Timer(constants.RE_TRAIN_INTERVAL_SEC, do_update)
        updating_thread.start()

    def do_update_start():
        # Do initialisation stuff here
        global updating_thread
        # Create your thread
        updating_thread = threading.Timer(constants.RE_TRAIN_INTERVAL_SEC, do_update)
        updating_thread.start()

    # Initiate
    do_update_start()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
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
            cv2.imwrite(constants.IMAGES_DIRECTORY + str(num) + str(file_name), img=result)

    return jsonify({"resp": "Hello World"})


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    _response_format = ResponseFormat(ids=[], count=0, message="works well!", error_code=0)
    file_logger.info("works well!")
    return jsonify(_response_format.__dict__)
