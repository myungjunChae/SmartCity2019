# image_detector.py

from object_detector import *
import cv2
import numpy as np
import sys
import argparse
import os
import json
from os import walk


def behavior_estimate(all_estimate):
    size = len(all_estimate)

    for index, all_estimate in enumerate(all_estimate):
        print(index, all_estimate)

    with open('/home/cmj9597/server/data/data.json', 'w') as f:
        json.dump([1, 2, 3], f)


if __name__ == '__main__':
    # get image for dir
    image_file = []
    walkPath = '/home/cmj9597/server/object_detection_tensorflow/saved_image'

    for (dirpath, dirnames, filenames) in walk(walkPath):
        image_file = list(map(lambda i: dirpath + '/' + i, filenames))
        break

    # goods detection
    goods_detector = ObjectDetector(
        MODEL_PATH='/home/cmj9597/server/object_detection_tensorflow/models/goods/', NUM_CLASSES=7)

    # hands detection
    hands_detector = ObjectDetector(
        MODEL_PATH='/home/cmj9597/server/object_detection_tensorflow/models/hands/', NUM_CLASSES=1)

    # Machine Learning
    all_estimate = []
    for image in image_file:
        cv = cv2.imread(image, cv2.IMREAD_COLOR)
        height, width = cv.shape[:2]
        #print("image file:", image, "(%dx%d)" % (width, height))

        # object detecting
        goods_result = goods_detector.detect_objects(cv)
        hands_result = hands_detector.detect_objects(cv)

        # data processing
        estimate = {'hands': 0,
                    'goods': 0,
                    'detail': goods_result}

        if len(hands_result) is not 0:
            estimate['hands'] = 1

        if len(goods_result) is not 0:
            estimate['goods'] = 1

        # final result
        all_estimate.append(estimate)

    behavior_estimate(all_estimate)
