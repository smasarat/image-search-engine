import cv2
import os
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request
import numpy as np
from key_constants import constants
from querying.searcher import Searcher
from response_format.response import ResponseFormat
from training.descriptor import ColorDescriptor
from logs.log_config import LOGGING
from logging.config import dictConfig
import logging

dictConfig(LOGGING)
file_logger = logging.getLogger("file")

app = Flask(__name__)

if __name__ == '__main__':
    app.run()


@app.route('/upload', methods=['POST'])
def get_similar_images():
    file = request.files['file']
    npimg = np.fromstring(file.read(), np.uint8)
    # convert numpy array to image
    query = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    cd = ColorDescriptor((8, 12, 3))
    features = cd.describe(query)

    # perform the search
    searcher = Searcher(indexPath=constants.TMP_FILE_TO_STORE_DESCRIPTIONS)
    results = searcher.search(features)

    tmp_name = file.filename
    file.stream.seek(0)
    file.save(constants.IMAGES_DIRECTORY + str(tmp_name))

    num = 0
    for (score, result_path) in results:
        num += 1
        # load the result image and display it
        result = cv2.imread(result_path)
        cv2.imwrite(constants.IMAGES_DIRECTORY + str(num) + str(tmp_name), img=result)

    return jsonify({"resp": "Hello World"})


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    _response_format = ResponseFormat(ids=[], count=0, message="works well!", error_code=0)
    file_logger.info("works well!")
    return jsonify(_response_format.__dict__)
