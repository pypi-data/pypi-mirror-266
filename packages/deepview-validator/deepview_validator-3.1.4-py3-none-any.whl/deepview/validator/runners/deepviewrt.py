# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import UnsupportedNormalizationException
from deepview.validator.exceptions import UnsupportedEngineException
from deepview.validator.exceptions import NonMatchingIndexException
from deepview.validator.exceptions import UnsupportedNMSException
from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.writers.core import Writer
from deepview.validator.runners.core import Runner
from time import monotonic_ns as clock_now
from os.path import exists
from timeit import timeit
import numpy as np


class DeepViewRTRunner(Runner):
    """
    Runs DeepViewRT models using the VAAL API.
    
    Parameters
    ----------
        model_path: str
            The path to the model.

        labels: list
            Unique string labels.

        max_detections: int
            The maximum detections to output.

        warmup: int
            The number of warmup iterations to perform.

        engine: str
            The type of engine to run the model (cpu, npu, gpu).

        norm: str
            The type of image normalization to perform
            (raw, unsigned, signed, whitening, imagenet).

        nms_type: str
            The type of non max supression to perform (standard, fast, matrix).

        detection_score_threshold: float
            NMS score threshold from 0 to 1.

        detection_iou_threshold: float
            NMS iou threshold from 0 to 1.

        label_offset: int
            The index offset to match label index to the ground truth index.

        box_format: str
            The box format to output the model predictions.

    Raises
    ------
        UnsupportedNormalizationException
            Raised if the passed image normalization is not recognized.

        UnsupportedEngineException
            Raised if the passed engine is not recognized.

        NonMatchingIndexException
            Raised if the model outputs an index
            that is out of bounds to the labels list passed
            or the labels contained within the model itself.

        UnsupportedNMSException
            Raised if the NMS provided is not recognized.

        MissingLibraryException
            Raised if the deepview.vaal library is not found.

        NotImplementedError
            Some methods have not been implemented yet.

        ValueError
            Raised if the provided image_path
            does not exist and the provided image is not a numpy.ndarray.
    """
    def __init__(
        self,
        model_path,
        labels,
        max_detections,
        warmup=0,
        engine='npu',
        norm='raw',
        nms_type=None,
        detection_score_threshold=0.5,
        detection_iou_threshold=0.5,
        label_offset=0,
        box_format='xyxy'
    ):
        super(DeepViewRTRunner, self).__init__(model_path)

        self.labels = labels
        self.label_offset = label_offset
        self.max_detections = max_detections
        
        try:
            import deepview.vaal as vaal
        except ImportError:
            raise MissingLibraryException(
                "vaal library is needed to run DeepViewRT models.")

        if engine.lower() not in ['npu', 'cpu', 'gpu']:
            raise UnsupportedEngineException(engine)

        try:
            self.ctx = vaal.Context(engine)
        except AttributeError:
            raise EnvironmentError(
                'Did not find Vaal Context. Try setting the environment \
                    variable VAAL_LIBRARY to the VAAL library.')
        self.device = self.ctx.device

        if max_detections is not None:
            self.ctx['max_detection'] = max_detections

        self.detection_threshold = detection_score_threshold
        self.detection_iou = detection_iou_threshold
        self.ctx['score_threshold'] = detection_score_threshold
        self.ctx['iou_threshold'] = detection_iou_threshold
        self.ctx['box_format'] = box_format

        if nms_type is not None:
            if nms_type.lower() not in [
                'standard', 'fast', 'matrix', 'tensorflow']:
                raise UnsupportedNMSException(nms_type)
            elif nms_type.lower() in ['standard', 'fast', 'matrix']:
                self.ctx['nms_type'] = nms_type
            self.nms_type = nms_type
        else:
            self.nms_type = 'fast'

        if norm.lower() not in [
            'raw',
            'signed',
            'unsigned',
            'whitening',
            'imagenet']:
            raise UnsupportedNormalizationException(self.norm)
       
        if norm is not None:
            if norm == 'raw':
                self.ctx['proc'] = vaal.ImageProc.RAW
            elif norm == 'signed':
                self.ctx['proc'] = vaal.ImageProc.SIGNED_NORM
            elif norm == 'unsigned':
                self.ctx['proc'] = vaal.ImageProc.UNSIGNED_NORM
            elif norm == 'whitening':
                self.ctx['proc'] = vaal.ImageProc.WHITENING
            elif norm == 'imagenet':
                self.ctx['proc'] = vaal.ImageProc.IMAGENET
            else:
                Writer.logger(
                    f"Unsupported normalization method: {norm}", code="ERROR")

        self.ctx.load_model(model_path)
        if int(warmup) > 0:
            Writer.logger("Loading model and warmup...", code="INFO")
            t = timeit(self.ctx.run_model, number=warmup)
            Writer.logger("model warmup took %f seconds (%f ms avg)\n" %
                          (t, t * 1000 / warmup), code="INFO")

    def run_single_instance(self, image):
        """
        Runs deepviewrt models and parses the prediction \
            bounding boxes, scores, and labels and records timings \
                (load, inference, box).
        
        Parameters
        ----------
            image: str or np.ndarray
                If the dataset is Darknet, then the image path is used which
                is a string.
                If the dataset is TFRecords, then the image is a
                np.ndarray.

        Returns
        -------
            boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            ValueError
                Raised if the provided image_path
                does not exist and the provided image is not a numpy.ndarray.
        """
        if isinstance(image, str):
            start = clock_now()
            if exists(image):
                self.ctx.load_image(image)
            else:
                raise ValueError(
                    "The provided image path does not exist at: {}".format(
                        image))
            load_ns = clock_now() - start
        elif isinstance(image, np.ndarray):
            start = clock_now()
            rgba_image = np.concatenate(
                (image, np.zeros((image.shape[0], image.shape[1], 1))), axis=2)
            self.ctx.load_image(rgba_image.astype(np.uint8))
            load_ns = clock_now() - start
        else:
            raise ValueError(
                "The provided image is neither a path nor a np.ndarray. " +
                "Provided with type: {}".format(type(image)))
        self.loading_input_timings.append(load_ns * 1e-6)

        start = clock_now()
        self.ctx.run_model()
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

        start = clock_now()
        if self.nms_type.lower() == "tensorflow": 
            outputs = list()
            for i in range(4):
                out = self.ctx.output(index=i)
                if out is not None:
                    outputs.append(out.dequantize().array())
        else:
            outputs = self.ctx.boxes()
        boxes_ns = clock_now() - start
        self.box_timings.append(boxes_ns * 1e-6)
        outputs = self.postprocessing(outputs)
        return outputs

    def postprocessing(self, outputs):
        """
        Collects the bounding boxes, scores and labels for the image.
       
        Parameters
        ----------
            outputs: list
                This contains bounding boxes, scores, labels.

        Returns
        -------
            boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            NonMatchingIndexException
                Raised if the model label
                index is out of bounds to the input labels list
                or the unique labels contained within the model.
        """
        if self.nms_type.lower() == "tensorflow":
            boxes, scores = None, None
            for out in outputs:
                if len(out.shape) == 3:
                    scores = out
                    continue
                if out.shape[-1] == 4 and out.shape[-2] == 1:
                    boxes = out
                    continue
            boxes, classes, scores = self.process_tensorflow_nms(boxes, scores)
        else:
            boxes, classes, scores = list(), list(), list()
            for box in outputs:
                output = self.process_vaal_nms(box)
                if output is not None:
                    label, box, score = output
                    classes.append(label)
                    boxes.append(box)
                    scores.append(score)
                else:
                    return output
        boxes = np.array(boxes)
        classes = np.array(classes)
        scores = np.array(scores)
        return boxes, classes, scores
    
    def process_vaal_nms(self, box):
        """
        Processes model detections using the VAAL NMS.

        Parameters
        ----------
            box: deepview.vaal.library.VAALBox
                This contains the label, box, and score from the model.

        Returns
        -------
            The NMS processed label, box, and score.

        Raises
        ------
            NonMatchingIndexException
                Raised if the label index 
                returned by the model does not match any index position in
                either context labels or the provided labels from the dataset.
        """
        label = box.label + self.label_offset
        if label >= 0:
            if len(self.ctx.labels):
                try:
                    if self.ctx.label(label) == "VisionPack Trial Expired":
                        return None
                    else:
                        dt_class = self.ctx.label(label).lower().rstrip(
                            '\"').lstrip('\"')
                except IndexError:
                    raise NonMatchingIndexException(label)
            elif len(self.labels):
                try:
                    dt_class = self.labels[label].lower().rstrip(
                        '\"').lstrip('\"')
                except IndexError:
                    raise NonMatchingIndexException(label)
            else:
                dt_class = label
            dt_box = [box.xmin, box.ymin, box.xmax, box.ymax]
            dt_score = box.score
            return dt_class, dt_box, dt_score
            
    def process_tensorflow_nms(self, boxes, scores):
        """
        Processes model detections using tensorflow NMS.
       
        Parameters
        ----------
            boxes: np.ndarray
                This array contains the bounding boxes for one image.
            
            scores: np.ndarray
                This array contains the model score per bounding box.

        Returns
        -------
            labels, bounding boxes, scores: np.ndarray
                These are the model detections after being processed using
                tensorflow NMS.
        
        Raises
        ------
            NonMatchingIndexException
                Raised if the model label index does
                not match any index position in the provided labels from
                the dataset. 
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            pass
        
        

        if self.label_offset > 0:
            scores = scores[..., self.label_offset:]

        nmsed_boxes, nmsed_scores, nmsed_classes, valid_boxes = \
                tf.image.combined_non_max_suppression(
                boxes.astype(np.float32),
                scores.astype(np.float32),
                100,
                100,
                iou_threshold=self.detection_iou,
                score_threshold=self.detection_threshold)
        
        nmsed_boxes = nmsed_boxes.numpy()
        nmsed_classes = tf.cast(nmsed_classes, tf.int32)

        nms_predicted_boxes = [nmsed_boxes[i, :valid_boxes[i], :]
                            for i in range(nmsed_boxes.shape[0])][0]
        nms_predicted_classes = [nmsed_classes.numpy()[i, :valid_boxes[i]]
                                for i in range(nmsed_classes.shape[0])][0]
        nms_predicted_scores = [nmsed_scores.numpy()[i, :valid_boxes[i]]
                                for i in range(nmsed_scores.shape[0])][0]

        if len(self.labels):
            string_nms_predicted_classes = list()
            format_nms_predicted_boxes = list()
            for cls, box in zip(nms_predicted_classes, nms_predicted_boxes):
                try:
                    string_nms_predicted_classes.append(
                        self.labels[int(cls)])
                except IndexError:
                    raise NonMatchingIndexException(cls)
                format_nms_predicted_boxes.append(box)
            nms_predicted_classes = np.array(string_nms_predicted_classes)
            nms_predicted_boxes = np.array(format_nms_predicted_boxes)
        
        return nms_predicted_boxes, nms_predicted_classes, nms_predicted_scores

    def get_input_type(self):
        """
        Returns the model input type.
        
        Parameters
        ----------
            None

        Returns
        -------
            type: str
                The model input type

        Raises
        ------
            NotImplementedError
                raise because it has not been implemented yet.
        """
        raise NotImplementedError("has not been implemented.")

    def get_output_type(self):
        """
        Returns the model output type.
       
        Parameters
        ----------
            None

        Returns
        -------
            type: str
                The model output type

        Raises
        ------
            NotImplementedError
                raise because it has not been implemented yet.
        """
        raise NotImplementedError("has not been implemented.")

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

        Raises
        ------
            None
        """
        return self.ctx.tensor('serving_default_input_1:0').shape