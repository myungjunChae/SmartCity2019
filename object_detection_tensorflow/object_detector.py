# object_detector.py

import cv2
import os
import numpy as np
import tensorflow as tf
import tarfile
import six.moves.urllib as urllib
import six
import time

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import ops as utils_ops


class ObjectDetector():
    GRAPH_FILE_NAME = 'frozen_inference_graph.pb'
    LABEL_FILE_NAME = 'label_map.pbtxt'

    def __init__(self, MODEL_PATH, NUM_CLASSES):
        # Initialize some variables
        # print("ObjectDetector('%s', '%s')" % (model_name, label_file))
        self.process_this_frame = True

        # set frozen graph
        # TODO : 모델 폴더 내에 그래프 파일(export)
        self.graph_file = MODEL_PATH + '/' + self.GRAPH_FILE_NAME

        # Load a (frozen) Tensorflow model into memory.
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.graph_file, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            graph = self.detection_graph

            ops = graph.get_operations()
            all_tensor_names = {
                output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = graph.get_tensor_by_name(tensor_name)

            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(
                    tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(
                    tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(
                    tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [
                                           real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [
                                           real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, 480, 640)
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)

            self.tensor_dict = tensor_dict

        self.sess = tf.Session(graph=self.detection_graph)

        # Loading label map
        # Label maps map indices to category names,
        # so that when our convolution network predicts `5`,
        # we know that this corresponds to `airplane`.
        # Here we use internal utility functions,
        # but anything that returns a dictionary mapping integers to appropriate string labels would be fine
        label_map = label_map_util.load_labelmap(
            MODEL_PATH + self.LABEL_FILE_NAME)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        self.output_dict = None

        self.last_inference_time = 0

    def run_inference(self, image_np):
        sess = self.sess
        graph = self.detection_graph
        with graph.as_default():
            image_tensor = graph.get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(self.tensor_dict,
                                   feed_dict={image_tensor: np.expand_dims(image_np, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(
                output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]

        return output_dict

    def time_to_run_inference(self):
        unixtime = int(time.time())
        if self.last_inference_time != unixtime:
            self.last_inference_time = unixtime
            return True
        return False

    def detect_objects(self, frame):
        time1 = time.time()
        # Grab a single frame of video

        # Resize frame of video to 1/4 size for faster face recognition processing
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        small_frame = frame

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        time2 = time.time()

        # Only process every other frame of video to save time
        if self.time_to_run_inference():
            self.output_dict = self.run_inference(rgb_small_frame)

        time3 = time.time()

        max_boxes_to_draw = 20
        min_score_thresh = .5
        image = frame
        boxes = self.output_dict['detection_boxes']
        classes = self.output_dict['detection_classes']
        scores = self.output_dict['detection_scores']
        category_index = self.category_index
        # print("--------parsing--------")

        resultArray = []
        for i in range(min(max_boxes_to_draw, boxes.shape[0])):
            if scores is None or scores[i] > min_score_thresh:
                if classes[i] in six.viewkeys(category_index):
                    parsing_class = category_index[classes[i]]['name']
                else:
                    parsing_class = 'N/A'
                try:
                    parsing_score = '{}'.format(int(100 * scores[i]))
                except:
                    parsing_score = 'N/A'

                resultArray.append([parsing_class, parsing_score])
                # print('{} : {}%'.format(parsing_class, parsing_score))

        time4 = time.time()

        # print("%0.3f, %0.3f, %0.3f sec" %
        #      (time2 - time1, time3 - time2, time4 - time3))
        return resultArray

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()


if __name__ == '__main__':
    import camera

    # detector = ObjectDetector('ssd_mobilenet_v1_coco_2017_11_17')
    # detector = ObjectDetector('mask_rcnn_inception_v2_coco_2018_01_28')
    # detector = ObjectDetector('pet', label_file='data/pet_label_map.pbtxt')

    # Using OpenCV to capture from device 0. If you have trouble capturing
    # from a webcam, comment the line below out and use a video file
    # instead.
    cam = camera.VideoCamera()

    print("press `q` to quit")
    while True:
        frame = cam.get_frame()
        frame = detector.detect_objects(frame)

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')
