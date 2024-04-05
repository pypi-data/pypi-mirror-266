# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.runners.core import Runner
from deepview.validator.datasets import Dataset
from deepview.validator.writers import Writer
from time import monotonic_ns as clock_now
from timeit import timeit
import numpy as np

class TFliteRunner(Runner):
    """
    Runs TensorFlow Lite models.
    
    Parameters
    ----------
        model_path: str
            The path to the model.

        warmup: int
            The number of warmup iterations to perform.

        anchors: str
            The path to the anchors file.

        ext_delegates: str
            The path to the delegates file.

        num_threads: int

        embedded_nms: bool
            True if the model has embedded NMS, False otherwise.

        labels: list
            Unique string labels.

        detection_score_threshold: float
            NMS score threshold from 0 to 1.

        detection_iou_threshold: float
            NMS iou threshold from 0 to 1.

        norm: str
            The type of image normalization to perform (raw, unsigned, signed).

        label_offset: int
            The index offset to match label index to the ground truth index.

    Raises
    ------
        MissingLibraryException
            Raised if tflite_runtime library is not intalled.

        ValueError
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
    """
    def __init__(
        self,
        model_path,
        warmup,
        anchors,
        ext_delegate,
        num_threads,
        embedded_nms,
        labels,
        detection_score_threshold=0.5,
        detection_iou_threshold=0.5,
        norm='raw',
        label_offset=0
    ):
        super(TFliteRunner, self).__init__(model_path=model_path)
        self.interpreter = None
        self.model_path = model_path
        self.iou_threshold = detection_iou_threshold
        self.score_threshold = detection_score_threshold
        self.norm = norm.lower()
        self.warmup = warmup
        self.anchors = anchors
        self.ext_delegate = ext_delegate
        self.num_threads = num_threads
        self.embedded_nms = embedded_nms
        self.labels = labels
        self.label_offset = label_offset

    def load_model(self):
        """
        Loads the TFLite model.

        Parameters
        ----------
            None

        Returns
        -------
            None

        Raises
        ------
            MissingLibraryException
                Raised if tflite_runtime library is not intalled.
        """
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            raise MissingLibraryException(
                "tflite_runtime is needed to load TFlite models.")

        ext_delegate_options = {}

        Writer.logger(
            f"Loading external delegate from {self.ext_delegate}",
            code="INFO")
        ext_delegate = [
            tflite.load_delegate(
                self.ext_delegate,
                ext_delegate_options)]

        self.interpreter = tflite.Interpreter(
            model_path=self.model_path,
            experimental_delegates=ext_delegate,
            num_threads=self.num_threads
        )
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        scale_1 = self.output_details[0]['quantization_parameters']['scales']
        zp_1 = self.output_details[0]['quantization_parameters']['zero_points']

        scale_2 = self.output_details[1]['quantization_parameters']['scales']
        zp_2 = self.output_details[1]['quantization_parameters']['zero_points']
        # check the type of the input tensor
        input_type = self.input_details[0]['dtype']

        if self.warmup > 0:
            self.messenger("Loading model and warmup...", code="INFO")
            t = timeit(self.interpreter.invoke, number=self.warmup)
            self.messenger("model warmup took %f seconds (%f ms avg)" %
                           (t, t * 1000 / self.warmup), code="INFO")
        priors = np.load(self.anchors)

    def run_single_instance(self, image):
        """
        Produce tflite predictions on one image and records the timings.
       
        Parameters
        ----------
            image: str
                The path to the image.

        Returns
        -------
            nmsed_boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            nmsed_classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            nmsed_scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            ValueError
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
        """
        start = clock_now()
        image = Dataset.resize(image, self.get_input_shape())
        img = self.apply_normalization(image, self.norm)
        input_data = np.expand_dims(img, axis=0).astype(np.uint8)
        self.interpreter.set_tensor(
            self.input_details[0]['index'],
            input_data)
        load_ns = clock_now() - start
        self.loading_input_timings.append(load_ns)

        start = clock_now()
        self.interpreter.invoke()
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns)

        start = clock_now()
        boxes, labels, confidences = self.embed_nms()
        nmsed_boxes, nmsed_classes, nmsed_scores = self.postprocessing(
            (boxes, labels, confidences))
        decoder_ns = clock_now() - start
        self.box_timings.append(decoder_ns)
        return nmsed_boxes, nmsed_classes, nmsed_scores

    def embed_nms(self):
        """
        Performs embedded NMS operations for models that \
            don't have embedded NMS. If models already have embedded NMS, \
                then do not perform the combined non max suppression.
       
        Parameters
        ----------
            None

        Returns
        -------
            nmsed_boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            nmsed_classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            nmsed_scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow library is not intalled.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to perform NMS operations.")

        if self.embedded_nms:
            x1 = self.interpreter.get_tensor(self.output_details[0]['index'])
            x2 = self.interpreter.get_tensor(self.output_details[1]['index'])
            x3 = self.interpreter.get_tensor(self.output_details[2]['index'])

            boxes, labels, confidences = x1[0], x2[0], x3[0]
            return boxes, labels, confidences

        x1 = self.interpreter.get_tensor(
            self.output_details[0]['index']).astype(
            np.float32)
        x1 = (x1 + 67) * 0.00823736
        x2 = self.interpreter.get_tensor(
            self.output_details[1]['index']).astype(
            np.float32)
        x2 = (x2 + 128) * 0.00368589

        if x1.shape[-1] == 4 and x1.shape[-2] == 1:
            boxes = x1.reshape(1, -1, 4)
            confidences = x2
        else:
            boxes = x2.reshape(1, -1, 4)
            confidences = x1
        boxes = tf.expand_dims(boxes, 2)

        nmsed_boxes, nmsed_scores, nmsed_classes, valid_boxes = \
            tf.image.combined_non_max_suppression(
                boxes,
                confidences,
                100,
                100,
                score_threshold=self.score_threshold,
                iou_threshold=self.iou_threshold,
                clip_boxes=False)

        nmsed_classes = tf.cast(nmsed_classes, tf.int32) + self.label_offset

        nmsed_boxes = tf.keras.backend.stack([
            nmsed_boxes[:, :, 0] * 320,
            nmsed_boxes[:, :, 1] * 320,
            nmsed_boxes[:, :, 2] * 320,
            nmsed_boxes[:, :, 3] * 320
        ], axis=2)

        nmsed_boxes = [
            nmsed_boxes.numpy().astype(
                np.int32)[
                i,
                :valid_boxes[i],
                :] for i in range(
                nmsed_boxes.shape[0])][0]
        nmsed_scores = [nmsed_scores.numpy()[i, :valid_boxes[i]]
                        for i in range(nmsed_scores.shape[0])][0]
        nmsed_classes = [nmsed_classes.numpy()[i, :valid_boxes[i]]
                         for i in range(nmsed_classes.shape[0])][0]
        return nmsed_boxes, nmsed_classes, nmsed_scores

    def postprocessing(self, outputs):
        """
        Retrieves the boxes, scores and labels.

        Parameters
        ----------
            outputs:
                This contains bounding boxes, scores, labels.

        Returns
        -------
            nmsed_boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            nmsed_classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            nmsed_scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            None
        """
        if self.embedded_nms:
            boxes, confidences, labels = outputs
            nmsed_boxes, nmsed_scores, nmsed_classes = list(), list(), list()
            # Remove background
            for box, score, label in zip(boxes, confidences, labels):

                nmsed_boxes.append([box[1], box[0], box[3], box[2]])
                nmsed_classes.append(self.labels[int(label)])
                nmsed_scores.append(score)

            return np.array(nmsed_boxes), np.array(nmsed_classes), \
                np.array(nmsed_scores)

        nmsed_boxes, nmsed_scores, nmsed_classes = outputs
        # Remove background
        nmsed_boxes_copy = list()
        height, width = self.get_input_shape()
        for i in range(len(nmsed_classes)):
            if i in np.where(nmsed_classes == 0)[0].tolist():
                continue

            nmsed_boxes_copy.append([
                                    nmsed_boxes[i][0] / width,
                                    nmsed_boxes[i][1] / height,
                                    nmsed_boxes[i][2] / width,
                                    nmsed_boxes[i][3] / height
                                    ])

        nmsed_boxes = nmsed_boxes_copy
        nmsed_scores = np.delete(nmsed_scores, np.where(nmsed_classes == 0)[0])
        nmsed_classes = np.delete(nmsed_classes, np.where(nmsed_classes == 0))

        nms_predicted_classes = np.array(
            [self.labels[int(cls)].lower() for cls in nms_predicted_classes])

        return np.array(nmsed_boxes), nms_predicted_classes, nmsed_scores

    def get_input_shape(self):
        """
        Grabs the model input shape.

        Parameters
        ----------
            None

        Returns
        -------
            type: tuple or list
                The model input shape.
                (height, width).

        Raises
        ------
            None
        """
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        return (self.height, self.width)