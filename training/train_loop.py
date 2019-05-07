# import the necessary packages
import logging
import numpy as np
from elasticsearch import Elasticsearch

from key_constants import constants
from training.descriptor import ColorDescriptor
import argparse
import glob
import cv2
import threading
import time
from logging.config import dictConfig
from logs.log_config import LOGGING

dictConfig(LOGGING)
logger = logging.getLogger("file")
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()


# ap.add_argument("-d", "--dataset", required=True, help="Path to the directory that contains the images to be indexed")
# ap.add_argument("-i", "--index", required=True, help="Path to where the computed index will be stored")

class AlwaysRunningClass(threading.Thread):

    def stop(self):
        self._running = False

    def run(self):
        try:
            logger.info("started running ....")
            # initialize the color descriptor
            color_descriptor = ColorDescriptor(constants.COLOR_DESCRIPTOR_TUPLE)
            # open the output index file for writing
            output = open(constants.TMP_FILE_TO_STORE_DESCRIPTIONS, "w")

            images_directory = constants.IMAGES_DIRECTORY
            training_img_directory = [f for f in glob.glob(images_directory + "/*.png")]
            training_img_directory += [f for f in glob.glob(images_directory + "/*.jpg")]
            training_img_directory += [f for f in glob.glob(images_directory + "/*.jpeg")]
            training_img_directory += [f for f in glob.glob(images_directory + "/*.Jpeg")]
            training_img_directory += [f for f in glob.glob(images_directory + "/*.JPEG")]
            training_img_directory += [f for f in glob.glob(images_directory + "/*.jpg")]
            training_img_directory += [f for f in glob.glob(images_directory + "/*.JPG")]

            # use glob to grab the image paths and loop over them
            counter = 0
            for image_path_iter in training_img_directory:
                counter += 1
                if counter % int(constants.TRAINING_LOG_THRESHOLD) == 0:
                    logger.info("describing in progress: {}".format(counter))
                # extract the image ID (i.e. the unique filename) from the image
                # path and load the image itself
                image_id = image_path_iter[image_path_iter.rfind("/") + 1:]
                image = cv2.imread(image_path_iter)

                # describe the image
                features = color_descriptor.describe(image)

                # write the features to file
                features = [f for f in features]
                try:
                    # output.write("%s,%s\n" % (imageID, ",".join(features)))
                    es = Elasticsearch(hosts=[{"host": constants.ES_HOST, "port": constants.ES_PORT}])
                    es.index(index=constants.ES_SE_INDEX, doc_type=constants.ES_SE_DESCRIPTOR, id=image_id,
                             body={"features": np.array(features).tolist()})
                except Exception as e:
                    logger.exception(e)

            # close the index file
            # output.close()

        except Exception as e:
            logger.exception(e)




# todo: set strategy for determine number of features in config file
# todo: check the possibility of working with different versions of Elasticsearch (7.0)
# todo: rename file_names to short format. (not complete address)