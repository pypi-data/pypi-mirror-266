# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import UnsupportedNormalizationException
from deepview.validator.exceptions import NonMatchingIndexException
from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.datasets.core import Dataset
from deepview.validator.runners.core import Runner
from time import monotonic_ns as clock_now
import numpy as np

class DetectionKerasRunner(Runner):
    """
    Runs the Keras (h5) models using the tensorflow library.
    
    Parameters
    ----------
        model_path: str
            The path to the model.

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

        max_detections: int, default 100
            Maximum number of detections used by TensorFlow NMS.

    Raises
    ------
        UnsupportedNormalizationException
            Raised if the passed image normalization is not recognized.

        NonMatchingIndexException
            Raised if the model outputs an index
            that is out of bounds to the labels list passed or the labels
            contained within the model itself.

        MissingLibraryException
            Raised if the tensorflow library is not installed.

        ValueError
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
    """
    def __init__(
        self,
        model_path,
        labels=None,
        detection_iou_threshold=0.5,
        detection_score_threshold=0.5,
        norm='unsigned',
        label_offset=0,
        max_detections=100
    ):
        super(DetectionKerasRunner, self).__init__(model_path)

        self.iou_threshold = detection_iou_threshold
        self.score_threshold = detection_score_threshold
        self.norm = norm.lower()
        self.labels = labels
        self.label_offset = label_offset
        self.max_detections = max_detections
        self.nms_type = "tensorflow"

        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to load the model.")
        
        if len(tf.config.list_physical_devices('GPU')):
            self.device = "gpu"
        elif len(tf.config.list_physical_devices('CPU')):
            self.device = "cpu"
        else:
            self.device = "unknown"

        if self.norm not in ['raw', 'signed', 'unsigned']:
            raise UnsupportedNormalizationException(norm)

    def load_model(self):
        """
        Loads the Keras model using tensorflow.

        Parameters
        ----------
            None

        Returns
        -------
            None

        Raises
        ------
            MissingLibraryException
                Raised if the tensorflow library is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to load the model.")
        self.model = tf.keras.models.load_model(self.source, compile=False)

    def run_single_instance(self, image):
        """
        Runs the model to produce predictions on a single image and \
            records the timing information of the model.

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
                Raised if the provided image is
                neither a string path that points to the image nor is it a
                numpy.ndarray. Furthermore it raise if the
                provided image path does not exist.
        """
        start = clock_now()
        image = Dataset.resize(image, self.get_input_shape())
        input_tensor = self.apply_normalization(image, self.norm)
        load_ns = clock_now() - start
        self.loading_input_timings.append(load_ns * 1e-6)

        start = clock_now()
        outputs = self.model.predict(input_tensor, verbose=0)
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

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
            outputs:
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
            MissingLibraryException
                Raised if the tensorflow library is not installed.

            NonMatchingIndexException
                Raised if the model label index is
                out of bounds to the input labels list.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to perform NMS operations.")

        boxes = outputs[-2]

        if self.label_offset > 0:
            scores = outputs[-1][..., self.label_offset:]
        else:
            scores = outputs[-1]

        nmsed_boxes, nmsed_scores, nmsed_classes, valid_boxes = \
            tf.image.combined_non_max_suppression(
                boxes,
                scores,
                self.max_detections,
                self.max_detections,
                iou_threshold=self.iou_threshold,
                score_threshold=self.score_threshold,
                clip_boxes=False)

        nmsed_boxes = nmsed_boxes.numpy()
        nmsed_classes = tf.cast(nmsed_classes, tf.int32)

        nms_predicted_boxes = [nmsed_boxes[i, :valid_boxes[i], :]
                               for i in range(nmsed_boxes.shape[0])][0]
        nms_predicted_classes = [nmsed_classes.numpy()[i, :valid_boxes[i]]
                                 for i in range(nmsed_classes.shape[0])][0]
        nms_predicted_scores = [nmsed_scores.numpy()[i, :valid_boxes[i]]
                                for i in range(nmsed_scores.shape[0])][0]

        if self.labels:
            string_nms_predicted_classes = list()
            for cls in nms_predicted_classes:
                try:
                    string_nms_predicted_classes.append(self.labels[int(cls)])
                except IndexError:
                    raise NonMatchingIndexException(cls)
            nms_predicted_classes = np.array(string_nms_predicted_classes)
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
                The model input type.

        Raises
        ------
            None
        """
        return 'float32'

    def get_output_type(self):
        """
        Returns the model output type.

        Parameters
        ----------
            None

        Returns
        -------
            type: str
                The model output type.

        Raises
        ------
            None
        """
        return 'float32'

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
        return self.model.input.shape[1:]
    
class InferenceKerasModel(DetectionKerasRunner):
    """
    Provides inference to the Keras Runner during model training.

    Parameters
    ----------
        model_path: tf.keras.model
            A tensorflow loaded model.

        labels: list
            Unique string or integer index labels.

        detection_score_threshold: float
            NMS score threshold from 0 to 1.

        detection_iou_threshold: float
            NMS iou threshold from 0 to 1.

        norm: str
            The type of image normalization to perform (raw, unsigned, signed).

        mode: str
            This specifies the model configuration under 'training' or by
            default under 'validation'. Validation is used in ModelPack
            internally when training models to determine the metrics
            after each epoch.

        label_offset: int
            The index offset to match label index to the ground truth index.

        max_detections: int, default 100
            Maximum number of detections used by TensorFlow NMS.

    Raises
    ------
        UnsupportedNormalizationException
            Raised if the passed image normalization is not recognized.

        NonMatchingIndexException
            Raised if the model outputs an index
            that is out of bounds to the labels list passed or
            the labels contained within the model itself.

        MissingLibraryException
            Raised if the tensorflow library is not installed.
    """
    def __init__(
            self,
            model,
            labels,
            detection_iou_threshold=0.5,
            detection_score_threshold=0.5,
            norm='unsigned',
            label_offset=0,
            max_detections=100
    ):
        super(InferenceKerasModel, self).__init__(
            model_path=model,
            labels=labels,
            detection_iou_threshold=detection_iou_threshold,
            detection_score_threshold=detection_score_threshold,
            norm=norm,
            label_offset=label_offset,
            max_detections=max_detections
        )

        self.model = model
        self.input_shape = self.model.input.shape[1:]

    def load_model(self):
        """Abstract Method"""
        pass

class SegmentationKerasRunner(Runner):
    """
    Runs Keras models to produce segmentation masks.
  
    Parameters
    -----------
        model_path: str
            The path to the Keras model.

    Raises
    ------
        MissingLibraryException:
            Raised if the the tensorflow library
            which is used to load and run a keras model is not installed.
    """
    def __init__(
            self, 
            model,
            norm='unsigned'
        ):
        super(SegmentationKerasRunner, self).__init__(source=model)

        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "Tensorflow i needed to load Keras models."
            )
        
        self.norm = norm
        
        if isinstance(model, str):
            self.model = tf.keras.models.load_model(model, compile=False)
        else:
            self.model = model

        if len(tf.config.list_physical_devices('GPU')):
            self.device = "gpu"
        elif len(tf.config.list_physical_devices('CPU')):
            self.device = "cpu"
        else:
            self.device = "unknown"

    def run_single_instance(self, image):
        """
        Runs the loaded Keras model on a single image \
            to produce a mask for the image.

        Parameters
        ----------
            image: str or np.ndarray
                If the dataset is Darknet, then the image path is used which
                is a string.
                If the dataset is TFRecords, then the image is a
                np.ndarray.

        Returns
        -------
            mask: np.ndarray
                This is the segmentation mask of the image 
                where each pixel is represented by a class in
                the image.

        Raises
        ------
            MissingLibraryException
                Raised if the tensorflow library 
                is not installed which is needed
                to run a Keras model.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "Tensorflow i needed to load Keras models.")

        start = clock_now()
        img = Dataset.resize(image, self.get_input_shape())
        tensor = self.apply_normalization(img, self.norm)
        load_ns = clock_now() - start
        self.loading_input_timings.append(load_ns * 1e-6)
    
        start = clock_now()
        output = self.model.predict(tensor, verbose=0)
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

        start = clock_now()
        mask = tf.argmax(output, axis=-1)[0].numpy().astype(np.uint8)
        boxes_ns = clock_now() - start
        self.box_timings.append(boxes_ns * 1e-6)
        return mask

    def get_input_shape(self):
        """
        Returns the input shape of the Keras model.

        Parameters
        ----------
            None
        
        Returns
        -------
            input shape: tuple
                This is the model input shape (height, width).
        
        Raises
        ------
            None
        """
        _, mH, mW, _ = self.model.input.shape
        return (mH, mW)

class PoseKerasRunner(Runner):
    """
    Runs Keras pose models.

    Parameters
    ----------
        model_path: str
            The path to the model.

        norm: str
            The type of image normalization to perform.

    Raises
    -------
        MissingLibraryException
            Raised if the tensorflow library is not installed.
    """
    def __init__(
            self, 
            model_path, 
            norm="unsigned"
        ):
        super(PoseKerasRunner, self).__init__(model_path)

        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to load the model.")
        
        if len(tf.config.list_physical_devices('GPU')):
            self.device = "gpu"
        elif len(tf.config.list_physical_devices('CPU')):
            self.device = "cpu"
        else:
            self.device = "unknown"

        if norm.lower() not in ['raw', 'signed', 'unsigned']:
            raise UnsupportedNormalizationException(norm)
        else:
            self.norm = norm.lower()

    def load_model(self):
        """
        Loads the Pose Keras model using tensorflow.

        Parameters
        ----------
            None

        Returns
        -------
            None

        Raises
        ------
            MissingLibraryException
                Raised if the tensorflow library is not installed.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(
                "tensorflow is needed to load the model.")
        self.model = tf.keras.models.load_model(self.source, compile=False)

    def run_single_instance(self, image):
        """
        Runs the model to produce predictions on a single image and \
            records the timing information of the model.

        Parameters
        ----------
            image: str or np.ndarray
                If the dataset is Darknet, then the image path is used which
                is a string.
                If the dataset is TFRecords, then the image is a
                np.ndarray.

        Returns
        -------
            angles: list
                The Euler angles roll, pitch, yaw.

            labels: list
                Contains the label ["helmet"] describing the angles.

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
        input_tensor = self.apply_normalization(image, self.norm)
        load_ns = clock_now() - start
        self.loading_input_timings.append(load_ns * 1e-6)

        start = clock_now()
        outputs = self.model.predict(input_tensor, verbose=0)
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

        start = clock_now()
        boxes_ns = clock_now() - start
        self.box_timings.append(boxes_ns * 1e-6)
        return outputs[0], None

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
        return self.model.input.shape[1:]
    
class InferencePoseModel(PoseKerasRunner):
    """
    Provides inference to the Keras Runner during model training.

    Parameters
    ----------
        model: 
            The path to the model.

        norm: str
            The type of image normalization to perform.

    Raises
    -------
        MissingLibraryException
            Raised if the tensorflow library is not installed.
    """
    UNSIGNED='unsigned'
    SIGNED='signed'
    RAW='raw'
    
    def __init__(
            self,
            model,
            norm='unsigned'
    ):
        super(InferencePoseModel, self).__init__(
            model_path=model,
            norm=norm
        )

        self.model = model
        self.input_shape = self.model.input.shape[1:]

    def load_model(self):
        """Abstract Method"""
        pass
    
    