# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import InvalidModelSourceException
from os.path import exists
import numpy as np

class Runner:
    """
    Abstract Class that provides a template \
        for the other runner classes.

    Parameters
    ----------
        source: str
            This is the path to the model, TRT engine,
            or a directory of text files.

    Raises
    ------
        InvalidModelSourceException
            Raised if source is None.

        FileNotFoundError
            Raised if the path to the model does not exist.
    """
    def __init__(
        self,
        source=None
    ):
        if source is None:
            raise InvalidModelSourceException(source)

        if isinstance(source, str):
            self.source = self.validate_model_path(source)
        else:
            self.model = source

        self.model = None
        self.input_shape = None
        self.device = None
        self.nms_type = None
        self.max_detections = None

        self.box_timings = list()
        self.inference_timings = list()
        self.loading_input_timings = list()

        self.sync_dict = {
            "motorbike": "motorcycle",
            "aeroplane": "airplane",
            "sofa": "couch",
            "pottedplant": "potted plant",
            "diningtable": "dining table",
            "tvmonitor": "tv"
        }
        self.load_model()

    @staticmethod
    def validate_model_path(source):
        """
        Validates the existance of the model path.
        
        Parameters
        ----------
            source: str
                This is the path to the model.

        Returns
        -------
            source: str
                The validated path to the model.

        Raises
        ------
            FileNotFoundError
                Raised if the path to the model does not exist.
        """
        if not exists(source):
            raise FileNotFoundError(
                "Model file is expected to be at: {}".format(source))
        return source

    def load_model(self):
        """Abstract Method"""
        pass

    def run_single_instance(self, image):
        """Abstract Method"""
        pass

    def postprocessing(self, outputs):
        """Abstract Method"""
        pass

    def get_input_type(self):
        """Abstract Method"""
        pass

    def get_output_type(self):
        """Abstract Method"""
        pass

    def get_input_shape(self):
        """Abstract Method"""
        pass

    @staticmethod
    def apply_normalization(image, norm_type):
        """
        Performs images normalizations (signed, unsigned, raw).

        Parameters
        ----------
            image: np.ndarray
                    The image to perform normalization.

        Returns
        -------
            image: np.ndarray
                Depending on the normalization, the image will be returned.

        Raises
        ------
            None
        """
        if norm_type == 'signed':
            return np.expand_dims((image / 127.5) - 1.0, 0).astype(np.float32)
        elif norm_type == 'unsigned':
            return np.expand_dims(image / 255.0, 0).astype(np.float32)
        else:
            return np.expand_dims(image, 0).astype(np.float32)

    @staticmethod
    def clamp(value, min=0, max=1):
        """
        Clamps a given value between 0 and 1 by default. 
        If the value is in between the set min and max, then it is returned.
        Otherwise it returns either min or max depending \
            on which is the closest.
    
        Parameters
        ----------
            value: float or int
                Value to clamp between 0 and 1 (defaults).

            min: int or float
                Minimum acceptable value.

            max: int or float
                Maximum acceptable value.

        Returns
        -------
            value: int or float
                This is the clamped value.

        Raises
        ------
            None
        """
        return min if value < min else max if value > max else value

    def summarize(self):
        """
        Returns a summary of all the timings:: \
            (mean, avg, max) of (load, inference, box).
       
        Parameters
        ----------
            None

        Returns
        -------
            timings in ms: dict

            .. code-block:: python

                {
                 'min_inference_time': minimum time to produce bounding boxes,
                 'max_inference_time': maximum time to produce bounding boxes,
                 'min_input_time': minimum time to load an image,
                 'max_input_time': maximum time to load an image,
                 'min_decoding_time': minimum time to process model
                                    predictions,
                 'max_decoding_time': maximum time to process model
                                    predictions,
                 'avg_decoding': average time to process model predictions,
                 'avg_input': average time to load an image,
                 'avg_inference': average time to produce bounding boxes,
                }

        Raises
        ------
            None
        """
        try:
            return {
                'min_inference_time': np.min(self.inference_timings),
                'max_inference_time': np.max(self.inference_timings),
                'min_input_time': np.min(self.loading_input_timings),
                'max_input_time': np.max(self.loading_input_timings),
                'min_decoding_time': np.min(self.box_timings),
                'max_decoding_time': np.max(self.box_timings),
                'avg_decoding': np.mean(self.box_timings),
                'avg_input': np.mean(self.loading_input_timings),
                'avg_inference': np.mean(self.inference_timings),
            }
        except ValueError:
            return None