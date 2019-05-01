# import the necessary packages
from key_constants import constants
from training.descriptor import ColorDescriptor
import argparse
import glob
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
# ap.add_argument("-d", "--dataset", required=True, help="Path to the directory that contains the images to be indexed")
# ap.add_argument("-i", "--index", required=True, help="Path to where the computed index will be stored")
args = vars(ap.parse_args())

# initialize the color descriptor
color_descriptor = ColorDescriptor((8, 12, 3))
# open the output index file for writing
output = open(constants.TMP_FILE_TO_STORE_DESCRIPTIONS, "w")

images_directory = constants.IMAGES_DIRECTORY
target_directory = [f for f in glob.glob(images_directory + "/*.png")]
target_directory += [f for f in glob.glob(images_directory + "/*.jpg")]

# use glob to grab the image paths and loop over them
for image_path_iter in target_directory:
    # extract the image ID (i.e. the unique filename) from the image
    # path and load the image itself
    imageID = image_path_iter[image_path_iter.rfind("/") + 1:]
    image = cv2.imread(image_path_iter)

    # describe the image
    features = color_descriptor.describe(image)

    # write the features to file
    features = [str(f) for f in features]
    output.write("%s,%s\n" % (imageID, ",".join(features)))

# close the index file
output.close()
