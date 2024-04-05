# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.runners.modelclient.core import ModelClientRunner
from deepview.validator.exceptions import NonMatchingIndexException
from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.datasets import Dataset
from time import monotonic_ns as clock_now
import requests as req
import numpy as np

class BoxesModelPack(ModelClientRunner):
    """
    Runs Yolo DeepViewRT models using modelrunner.
   
    Parameters
    ----------
        model_path: str
            This is the path to the model.

        target: str
            This is the modelrunner target in the EVK. Ex. 10.10.40.205:10817.

        labels: list
            This contains the unique string or integer index labels.

        detection_iou_threshold: float
            This is the NMS IoU threshold.

        detection_score_threshold: float
            This is the NMS score threshold.

        max_detections: int
            The maximum number of detections to consider per image.

        norm: str
            This is the input image normalization (raw, unsigned, signed).

        decoder: bool
            If True, this means an external decoder is needed. If False, the
            decoder is already embedded in the model.

        label_offset: int
            The index label offset to match to the ground truth index.

    Raises
    ------
        MissingLibraryException
            Raised if a required library is not installed.

        ValueError
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
    """
    def __init__(
        self,
        model_path,
        target,
        labels,
        detection_iou_threshold=0.5,
        detection_score_threshold=0.5,
        max_detections=25,
        norm='raw',
        decoder=False,
        label_offset=0
    ):
        super(BoxesModelPack, self).__init__(
            model_path=model_path,
            target=target)

        self.labels = labels
        self.iou_threshold = detection_iou_threshold
        self.score_threshold = detection_score_threshold
        self.max_detections = max_detections
        self.norm = norm
        self.label_offset = label_offset
        self.shape = (self.parameters.get('input_shape')[0], 
                    self.parameters.get('input_shape')[1])
        # TODO: Fix these hardcoded parameters or remove them entirely.
        self.decoder = decoder
        self.num_classes = 2
        self.anchors = np.array([
            0.23137255012989044 * (np.array([127, 110]) + 128),
            0.8549019694328308 * (np.array([-47, 127]) + 128),
            0.5176470875740051 * (np.array([77, 127]) + 128),
            1.2000000476837158 * (np.array([-9, 127]) + 128),
            1.4509804248809814 * (np.array([86, 127]) + 128),
            3.611764669418335 * (np.array([-12, 127]) + 128)
        ], dtype=np.float32).reshape(2, 3, 2)
        self.strides = np.array([16, 26], dtype=np.float32)
        self._scales = np.array([1.05, 1.05])
        
    def run_single_instance(self, image):
        """
        Runs the model to produce predictions on a single image.

        Parameters
        ----------
            image: str
                The path to the image.

        Returns
        -------
            boxes: np.ndarray
                This contains the bounding boxes [[box1], [box2], ...].

            classes: np.ndarray
                This contains the labels [cl1, cl2, ...].

            scores: np.ndarray
                This contains the scores [score, score, ...]

        Raises
        ------
            ValueError
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
        """
        start = clock_now()
        image = Dataset.resize(
            image, 
            (self.parameters.get('input_shape')[0], 
             self.parameters.get('input_shape')[1])
        )
        data = self.apply_normalization(
            image, 
            self.norm, 
            self.parameters.get('input_type').lower()
        )
        load_ns = clock_now() - start
        self.loading_input_timings.append(load_ns * 1e-6)

        start = clock_now()
        response = self.client.run(
            {
                self.parameters['input_name']: data
            },
            outputs=self.parameters.get('outputs').keys(),
            params={"run": 1}
        )
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

        start = clock_now()
        outputs = list()
        for name, parameters in self.parameters.get('outputs').items():
            shape = parameters.get('shape')
            labels_length = len(self.client.get_labels())
            if (len(shape) == 4 and shape[-1] == 4) or \
                (len(shape) == 3 and \
                 (shape[-1] in [labels_length, labels_length-1])):
                scale = parameters.get('scale')
                zp = parameters.get('zero_point')
                outputs.append(
                    scale * (response.get(name).astype(np.int32) - zp))
        boxes, classes, scores = self.postprocessing(outputs)
        boxes_ns = clock_now() - start
        self.box_timings.append(boxes_ns * 1e-6)
        return boxes, classes, scores

    def postprocessing(self, outputs):
        """
        Extracts the boxes, labels, and scores.
       
        Parameters
        ----------
            Outputs: np.ndarray
                This contains information regarding boxes,
                labels, and scores

        Returns
        -------
            boxes: np.ndarray
                This contains the bounding boxes [[box1], [box2], ...]

            classes: np.ndarray
                This contains the labels [cl1, cl2, ...]

            scores: np.ndarray
                This contains the scores [score, score, ...]

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to perform NMS operations.")

        if self.decoder:
            boxes, scores = self.build_decoder(
                [o.astype(np.float32) for o in outputs]
            )
        else:
            boxes = outputs[-2]
            scores = outputs[-1]

        nmsed_boxes, nmsed_scores, nmsed_classes, valid_boxes = \
            tf.image.combined_non_max_suppression(
                boxes,
                scores,
                self.max_detections,
                self.max_detections,
                iou_threshold=self.iou_threshold,
                score_threshold=self.score_threshold,
                clip_boxes=False
            )

        nmsed_boxes = nmsed_boxes.numpy()
        nmsed_classes = tf.cast(nmsed_classes, tf.int32) 

        nms_predicted_boxes = [nmsed_boxes[i, :valid_boxes[i], :]
                               for i in range(nmsed_boxes.shape[0])][0]
        nms_predicted_classes = [nmsed_classes.numpy()[i, :valid_boxes[i]]
                                 for i in range(nmsed_classes.shape[0])][0]
        nms_predicted_scores = [nmsed_scores.numpy()[i, :valid_boxes[i]]
                                for i in range(nmsed_scores.shape[0])][0]

        if len(self.client.get_labels()):
            labels = self.client.get_labels()
        elif len(self.labels):
            labels = self.labels
        
        if len(labels):
            string_nms_predicted_classes = list()
            for cls in nms_predicted_classes:
                try:
                    string_nms_predicted_classes.append(
                        labels[int(cls) + self.label_offset].lower().rstrip(
                            '\"').lstrip('\"'))
                except IndexError:
                    raise NonMatchingIndexException(cls)
            nms_predicted_classes = np.array(string_nms_predicted_classes)
        else:
            nms_predicted_classes = nms_predicted_classes + self.label_offset    
        return nms_predicted_boxes, nms_predicted_classes, nms_predicted_scores

    def build_decoder(self, outputs):
        """
        Builds the embeds decoder on the model.

        Parameters
        ----------
            Outputs: np.ndarray
                This contains information regarding boxes,
                labels, and scores.

        Returns
        -------
            boxes: np.ndarray
                This contains the bounding boxes [[box1], [box2], ...].

            scores: np.ndarray
                This contains the scores [score, score, ...].

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to build decoder.")

        bboxes1, scores1 = self.add_resolution_decoder(
            outputs[0],
            anchors=self.anchors[0],
            stride=self.strides[0],
            scale=self._scales[0])

        bboxes2, scores2 = self.add_resolution_decoder(
            outputs[1],
            anchors=self.anchors[1],
            stride=self.strides[1],
            scale=self._scales[1])

        box_xywh = tf.concat([bboxes1, bboxes2], axis=1, name='mpk_boxes')
        scores = tf.concat([scores1, scores2], axis=1, name='mpk_scores')

        boxes = tf.concat([
            (box_xywh[..., 0:1] - (box_xywh[..., 2:3] / 2.)) /
            self.shape[0],
            (box_xywh[..., 1:2] - (box_xywh[..., 3:4] / 2.)) /
            self.shape[1],
            (box_xywh[..., 0:1] + (box_xywh[..., 2:3] / 2.)) /
            self.shape[0],
            (box_xywh[..., 1:2] + (box_xywh[..., 3:4] / 2.)) /
            self.shape[1]
        ], axis=2)

        _, x1, x2, _ = outputs[0].shape
        _, y1, y2, _ = outputs[1].shape
        num_boxes = x1 * x2 * 3 + y1 * y2 * 3

        bboxes = tf.reshape(boxes, (-1, num_boxes, 1, 4))
        return bboxes, scores

    def add_resolution_decoder(self, output, anchors, stride, scale):
        """
        Adds resolution decoder to the model.

        Parameters
        ----------
            output: np.ndarray

            anchors: np.ndarray

            stride: np.ndarray

            scale: np.ndarray

        Returns
        -------
            pred_xywh

            pred_prob

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to add resolution decoder.")

        batch_size, output_height, output_width, _ = tf.shape(output)
        conv_raw_dxdy_0, conv_raw_dwdh_0, conv_raw_score_0, \
            conv_raw_dxdy_1, conv_raw_dwdh_1, conv_raw_score_1, \
            conv_raw_dxdy_2, conv_raw_dwdh_2, conv_raw_score_2 = tf.split(
                output,
                (2, 2, 1 + self.num_classes, 2, 2,
                 1 + self.num_classes,
                 2, 2, 1 + self.num_classes), axis=-1)

        conv_raw_score = [conv_raw_score_0, conv_raw_score_1, conv_raw_score_2]
        for idx, score in enumerate(conv_raw_score):
            score = tf.sigmoid(score)
            score = score[:, :, :, 0:1] * score[:, :, :, 1:]
            conv_raw_score[idx] = tf.reshape(
                score, (batch_size, -1, self.num_classes))
        pred_prob = tf.concat(conv_raw_score, axis=1)

        conv_raw_dwdh = [conv_raw_dwdh_0, conv_raw_dwdh_1, conv_raw_dwdh_2]
        for idx, dwdh in enumerate(conv_raw_dwdh):
            dwdh = tf.exp(dwdh)
            dwdh = dwdh * anchors[idx]
            conv_raw_dwdh[idx] = tf.reshape(dwdh, (batch_size, -1, 2))
        pred_wh = tf.concat(conv_raw_dwdh, axis=1)

        xy_grid = tf.meshgrid(tf.range(output_height), tf.range(output_width))
        xy_grid = tf.stack(xy_grid, axis=-1)
        xy_grid = tf.expand_dims(xy_grid, axis=0)
        xy_grid = tf.cast(xy_grid, tf.float32)

        conv_raw_dxdy = [conv_raw_dxdy_0, conv_raw_dxdy_1, conv_raw_dxdy_2]
        for idx, dxdy in enumerate(conv_raw_dxdy):
            dxdy = ((tf.sigmoid(dxdy) * scale) - 0.5 *
                    (scale - 1) + xy_grid) * stride
            conv_raw_dxdy[idx] = tf.reshape(dxdy, (batch_size, -1, 2))
        pred_xy = tf.concat(conv_raw_dxdy, axis=1)
        pred_xywh = tf.concat([pred_xy, pred_wh], axis=2)
        return pred_xywh, pred_prob

# TODO: Define a use case for this class or remove it entirely.
class BoxesYolo(ModelClientRunner):
    """
    Runs Yolo DeepViewRT models using modelrunner.

    Parameters
    ----------
        model_path: str
            This is the path to the model.

        target: str
            This is the modelrunner target in the EVK. Ex. 10.10.40.205:10817.

        labels: list
            This contains the unique string or integer index labels.

        detection_iou_threshold: float
            This is the NMS IoU threshold.

        detection_score_threshold: float
            This is the NMS score threshold.

        norm: str
            This is the input image normalization (raw, unsigned, signed).

        decoder: bool
            If True, this means an external decoder is needed. If False, the
            decoder is already embedded in the model.

        label_offset: int
            The index label offset to match to the ground truth index.

    Raises
    ------
        MissingLibraryException
            Raised if a required library is not installed.

        ValueError
            Raised if the provided image is
            neither a string path that points to the image nor is it a
            numpy.ndarray. Furthermore it raise if the
            provided image path does not exist.
    """
    def __init__(
        self,
        model_path,
        target,
        labels,
        detection_iou_threshold,
        detection_score_threshold,
        norm,
        decoder=False,
        label_offset=0
    ):
        super(BoxesYolo, self).__init__(
            model_path=model_path,
            target=target
        )
        self.labels = labels
        self.iou_threshold = detection_iou_threshold
        self.score_threshold = detection_score_threshold
        self.norm = norm
        self.decoder = decoder
        self.label_offset = label_offset

        self.num_classes = 2
        self.strides = [8, 16, 32]
        self.anchors = np.array([
            10, 13, 16, 30, 33, 23, 30, 61, 62, 45,
            59, 119, 116, 90, 156, 198, 373, 326
        ]).reshape(3, 1, 3, 1, 2)

    def run_single_instance(self, image):
        """
        Runs the model to produce predictions on a single image.
    
        Parameters
        ----------
            image: str
                The path to the image.

        Returns
        -------
            boxes: np.ndarray
                This contains the bounding boxes [[box1], [box2], ...].

            classes: np.ndarray
                This contains the labels [cl1, cl2, ...].

            scores: np.ndarray
                This contains the scores [score, score, ...].

        Raises
        ------
            ValueError
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
        """
        start = clock_now()
        shape = (self.shape[:2])
        image = Dataset.resize(image, (shape[1], shape[0]))
        data = np.expand_dims(image, 0).astype(np.uint8)
        load_ns = clock_now() - start
        self.loading_input_timings.append(load_ns * 1e-6)

        start = clock_now()
        self.parameters = self.read_quant_parameters(self.target)

        response = self.client.run(
            {self.parameters["input_name"]: data},
            outputs=[key for key in self.parameters['output_names']],
            params={"run": 1}
        )
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

        outputs = [response[key] for key in response.keys()]

        start = clock_now()
        boxes, classes, scores = self.postprocessing(outputs)
        boxes_ns = clock_now() - start
        self.box_timings.append(boxes_ns * 1e-6)
        return boxes, classes, scores

    def postprocessing(self, outputs):
        """
        Extracts the boxes, labels, and scores.

        Parameters
        ----------
            Outputs: np.ndarray
                This contains information regarding boxes,
                labels, and scores.

        Returns
        -------
            boxes: np.ndarray
                This contains the bounding boxes [[box1], [box2], ...].

            classes: np.ndarray
                This contains the labels [cl1, cl2, ...].

            scores: np.ndarray
                This contains the scores [score, score, ...].

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to perform NMS operations.")

        boxes, scores = self.get_boxes_scores(outputs, qunat=self.parameters)
        boxes = tf.expand_dims(boxes, 2)

        nmsed_boxes, nmsed_scores, nmsed_classes, valid_boxes = \
            tf.image.combined_non_max_suppression(
                boxes,
                scores,
                100,
                100,
                iou_threshold=self.iou_threshold,
                score_threshold=self.score_threshold,
                clip_boxes=False
            )

        nmsed_boxes = nmsed_boxes.numpy()
        nmsed_boxes = np.stack([
            nmsed_boxes[:, :, 0],
            nmsed_boxes[:, :, 1],
            nmsed_boxes[:, :, 2],
            nmsed_boxes[:, :, 3]

        ], axis=2).astype(np.float32)

        nms_predicted_boxes = [nmsed_boxes[i, :valid_boxes[i], :]
                               for i in range(nmsed_boxes.shape[0])][0]
        nms_predicted_classes = [nmsed_classes.numpy()[i, :valid_boxes[i]]
                                 for i in range(nmsed_classes.shape[0])][0]
        nms_predicted_scores = [nmsed_scores.numpy()[i, :valid_boxes[i]]
                                for i in range(nmsed_scores.shape[0])][0]

        nms_predicted_classes = np.array(
            [self.labels[int(cls) - 1].lower()
             for cls in nms_predicted_classes])
        return nms_predicted_boxes, nms_predicted_classes, nms_predicted_scores

    def read_quant_parameters(self, url):
        """
        Reads the model parameters from a given URL.

        Parameters
        ----------
            url: str
                Ex: http://10.10.40.205:10818/v1.

        Returns
        -------
            parameters: dict

        Raises
        ------
            ValueError
                Raised if the url provided is invalid.
        """
        response = req.get("{}/model".format(url))
        parameters = {}
        if response.status_code == 200:
            body = response.json()
            inputs = body['inputs']
            outputs = body['outputs']
            parameters['input_name'] = inputs[0]['name']
            parameters['input_type'] = inputs[0]['datatype']
            parameters['input_scale'] = inputs[0]['scale']
            parameters['input_zp'] = inputs[0]['zero_point']
            parameters['output_names'] = [key['name'] for key in outputs]
            parameters['output_scales'] = [key['scale'] for key in outputs]
            parameters['output_zp'] = [key['zero_point'] for key in outputs]
            parameters['output_type'] = outputs[0]['datatype']
        else:
            raise ValueError(
                "Bad url was provided and the model is not " +
                "running in specified target !")
        return parameters

    def get_boxes_scores(self, predictions, qunat=None):
        """
        Grabs the boxes and the scores.
       
        Parameters
        ----------
            predictions:

            qunat:

        Returns
        -------
            boxes: np.ndarray
                The model prediction bounding boxes.

            scores: np.ndarray
                The model prediction confidence scores.

        Raises
        ------
            None
        """

        if len(predictions) == 3:
            predictions = self.de_quantize(predictions, None)
            return self._predict(predictions)
        else:
            predictions = self.de_quantize(predictions, qunat)
            predictions = predictions[0] if len(
                predictions) == 1 else predictions
            boxes = self._xywh2xyxy(predictions[..., 0:4])
            probs = predictions[:, :, 4:5]
            classes = predictions[:, :, 5:]
            scores = probs * classes
            return boxes, scores

    def _predict(self, predictions, num_classes=1, num_fakes=5):
        """
        Performs the strides to align the predictions to the ground truth.
       
        Parameters
        ----------
            predictions:

            num_classes: int

            num_fakes: int

        Returns
        -------
            boxes: np.ndarray
                The model prediction bounding boxes.

            scores: np.ndarray
                The model prediction confidence scores.

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to get model predictions.")

        last_dim = num_fakes + num_classes
        imgsz = (
            predictions[0].shape[1] *
            self.strides[0],
            predictions[0].shape[2] *
            self.strides[0])

        grid = [tf.zeros(1)] * len(self.strides)
        for i in range(len(self.strides)):
            nx, ny = imgsz[0] // self.strides[i], imgsz[1] // self.strides[i]
            grid[i] = self._make_grid(nx, ny)

        z = []
        x = []
        for i in range(len(self.strides)):
            x.append(predictions[i])
            ny, nx = imgsz[0] // self.strides[i], imgsz[1] // self.strides[i]
            s = tf.reshape(x[i], [-1, ny * nx, 3, last_dim])
            x[i] = tf.transpose(s, [0, 2, 1, 3])

            y = tf.sigmoid(x[i])
            xy = (y[..., 0:2] * 2 - 0.5 + grid[i]) * self.strides[i]
            wh = (y[..., 2:4] * 2) ** 2 * tf.cast(self.anchors[i], tf.float32)
            xy /= tf.constant([[imgsz[1], imgsz[0]]], dtype=tf.float32)
            wh /= tf.constant([[imgsz[1], imgsz[0]]], dtype=tf.float32)
            y = tf.concat([xy, wh, y[..., 4:]], -1)
            z.append(tf.reshape(y, [-1, 3 * ny * nx, last_dim]))

        prediction = tf.concat(z, 1).numpy()

        boxes = self._xywh2xyxy(prediction[..., 0:4])
        probs = prediction[:, :, 4:5]
        classes = prediction[:, :, 5:]
        scores = probs * classes
        return boxes, scores

    def de_quantize(self, predictions, quant_params=None):
        """
        Performs dequantization.
        
        Parameters
        ----------
            predictions:

            qunat_params: dict

        Returns
        -------
            pp: list

            predictions:

        Raises
        ------
            None
        """
        if quant_params is None or quant_params['output_type'] == 'FLOAT32':
            return predictions
        else:
            pp = []
            scales = quant_params['output_scales']
            zps = quant_params['output_zp']
            for i, p in enumerate(predictions):
                float_val = scales[i] * (p - zps[i]).astype(np.float32)
                pp.append(float_val)
            return pp

    @staticmethod
    def _make_grid(ny=20, nx=20):
        """
        ...

        Parameters
        ----------
            ny: int

            nx: int

        Returns
        -------

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to make a meshgrid.")

        xv, yv = tf.meshgrid(tf.range(nx), tf.range(ny))
        return tf.cast(tf.reshape(tf.stack([xv, yv], 2), [
                       1, 1, ny * nx, 2]), dtype=tf.float32)

    @staticmethod
    def _xywh2xyxy(xywh):
        """
        ...

        Parameters
        ----------
            xywh:

        Returns
        -------

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed for prediction " +
                "annotation transformations.")

        x, y, w, h = tf.split(xywh, num_or_size_splits=4, axis=-1)
        return tf.concat([x - w / 2, y - h / 2, x + w / 2, y + h / 2], axis=-1)