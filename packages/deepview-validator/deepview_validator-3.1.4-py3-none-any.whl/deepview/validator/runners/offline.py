# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import UnsupportedAnnotationFormatException
from deepview.validator.exceptions import UnsupportedValidationTypeException
from deepview.validator.metrics.segmentationutils import create_mask_image
from deepview.validator.exceptions import NonMatchingIndexException
from os.path import basename, splitext, join, exists
from deepview.validator.datasets.core import Dataset
from deepview.validator.runners.core import Runner
import numpy as np
import warnings
import json

class OfflineRunner(Runner):
    """
    Reads model detection annotations stored that are in YOLO format. 
    For more information on the Yolo format visit:: \
        https://support.deepviewml.com/hc/en-us/articles/10869801702029
    Also reads model pose annotations in JSON files.
    For more information on the JSON pose annotations visit:: \
        https://support.deepviewml.com/hc/en-us/articles\
            /15626078040973-Headpose-dataset-format-for-ModelPack

    *Note: These text files should also include the model prediction scores \
        which adds to the Yolo format: [cls score xc yc width height].*

    Use Case: PT models are ran using https://github.com/ultralytics/yolov5 \
        repository. These model predictions will be stored in TXT files that \
            are in Yolo format. will read the text files to be validated.

    Parameters
    ----------
        annotation_source: str
            This is the path to the model prediction annotations
            stored in text files with yolo format annotations.
            [cls score xc yc width height].

        labels: list
            This contains the unique string labels in the dataset.

        validate_type: str
            This is the validation type being performed: detection, 
            segmentation or pose. 

        format: str
            Specify the format of the annotations (yolo, coco, pascalvoc).

        label_offset: int
            The index offset to match label index to the ground truth index.

    Raises
    ------
        UnsupportedAnnotationFormatException
            Raised if the annotation format passed
            is not recognized.

        NonMatchingIndexException
            Raised if the model outputs an index
            that is out of bounds to the labels list passed.

        UnsupportedValidationTypeException
                Raised if the provided validation type is not 
                recognized.
    """
    def __init__(
        self,
        annotation_source,
        labels,
        validate_type="detection",
        format='yolo',
        label_offset=0
    ):
        super(OfflineRunner, self).__init__(annotation_source)

        self.labels = labels
        self.validate_type = validate_type.lower()
        self.format = format
        self.label_offset = label_offset
        self.device = "cpu"

        if self.format not in ['yolo', 'pascalvoc', 'coco']:
            raise UnsupportedAnnotationFormatException(self.format)
        
        if self.validate_type == "detection":
            self.annotation_extension = "txt"
        elif self.validate_type == "pose" or \
                self.validate_type == "segmentation":
            self.annotation_extension = "json"
        else: 
            raise UnsupportedValidationTypeException(validate_type)

        self.transformer = None
        if self.format == 'yolo':
            self.transformer = Dataset.yolo2xyxy
        elif self.format == 'coco':
            self.transformer = Dataset.xywh2xyxy
        else:
            self.transformer = None

        self.denormalizer = None
        if validate_type == 'segmentation':
            self.denormalizer = Dataset.denormalize_polygon

    def run_single_instance(self, image):
        """
        Reads one prediction annotation file based on the \
            image name and returns the bounding boxes and labels for \
                detection, or the angles for pose, or the mask for \
                    segmentation.

        Parameters
        ----------
            image: str
                The path to the image. This is used to match the
                annotation to be read.

        Returns
        -------
            * Detection \
                boxes: np.ndarray
                    The prediction bounding boxes.. [[box1], [box2], ...].

                classes: np.ndarray
                    The prediction labels.. [cl1, cl2, ...].

                scores: np.ndarray
                    The prediction confidence scores.. [score, score, ...]
                    normalized between 0 and 1.

            * Pose: list
                [roll, pitch, yaw].

            * segmentation; dt_mask: np.ndarray
                This is the same resolution as the image with 
                container integers per element depending on the label to
                represent each pixel. 

        Raises
        ------
            NonMatchingIndexException
                Raised if the model outputs an index
                that is out of bounds to the labels list passed.

            ValueError
                Raised if the provided image is not a
                string path pointing to the image or if the provided path does
                not exist.

            UnsupportedValidationTypeException
                Raised if the provided validation type is not 
                recognized.
        """
        if isinstance(image, str):
            if exists(image):
                annotation_path = join(self.source, "{}.{}".format(
                    splitext(basename(image))[0], self.annotation_extension))
            else:
                raise ValueError(
                    "The provided image path does not exist at: {}".format(
                        image))
        else:
            raise ValueError(
                "The provided image needs to be a string path pointing " +
                "to the image. Provided with type: {}".format(type(image)))

        annotation = self.get_annotation(annotation_path)
        if annotation is None:
            if self.validate_type == "detection":
                return np.array([]), np.array([]), np.array([])
            elif self.validate_type == "pose":
                return np.array([]), np.array([])
            elif self.validate_type == "segmentation":
                return None
            else:
                raise UnsupportedValidationTypeException(self.validate_type)

        if self.validate_type == "detection":
            boxes, labels, scores = self.process_detection(annotation)
            return boxes, labels, scores
        
        elif self.validate_type == "pose":
            angles = self.process_pose(annotation)
            return angles, self.labels
        
        elif self.validate_type == "segmentation":
            dt_mask = self.process_segmentation(annotation)
            return dt_mask
        else:
            raise UnsupportedValidationTypeException(self.validate_type)
    
    def get_annotation(self, annotation_path):
        """
        Reads the annotatation path provided to get the information \
            stored in the file.

        Parameters
        ----------
            annotation_path: str
                This is the path to the annotation file.

        Returns
        -------
            annotation: np.ndarray, dict
                If detection \
                    [[cls, score, xc, yc, width, height], [...], [...], ...].
                
                If segmentation \
                
                    .. code-block:: python
                        
                        {
                            "dimension": [height, width],
                            "segment": [[[x, y], [x,y], ...], [...]] 
                            "labels": [int, int, int ...] 
                        }
                
                If pose \
                
                    .. code-block:: python

                        {
                            "angles": [[roll, pitch, yaw]]
                        }                         

        Raises
        ------
            UnsupportedValidationTypeException
                Raised if the provided validation type is not 
                recognized.
        """
        try:
            if self.validate_type == "detection":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    annotation = np.genfromtxt(annotation_path)
            elif self.validate_type == "pose" or \
                    self.validate_type == "segmentation":
                with open(annotation_path, "r") as fp:
                    annotation = json.load(fp)
            else:
                raise UnsupportedValidationTypeException(self.validate_type)
            return annotation
        except FileNotFoundError:
            return None

    def process_detection(self, annotation):
        """
        Parses the annotation to grab the detection bounding boxes, \
            scores, and labels.

        Parameters
        ----------
            annotation: np.ndarray
                [[cls, score, xc, yc, width, height], [...], [...], ...].

        Returns
        ------- 
            boxes: np.ndarray
                [[xmin, ymin, xmax, ymax], [...], ...]
            
            labels: np.ndarray
                [label, label, label, ...]

            scores: np.ndarray
                [score, score, score, ...]
        
        Raises
        ------
            NonMatchingIndexException
                Raised if the model outputs an index
                that is out of bounds to the labels list passed.
        """
        if len(annotation):
            annotation = annotation.reshape(-1, 6)
            boxes = annotation[:, 2:6]
            boxes = self.transformer(boxes) if self.transformer else boxes
        else:
            return np.array([]), np.array([]), np.array([])

        scores = annotation[:, 1:2].flatten().astype(np.float32)
        labels = annotation[:, 0:1].flatten().astype(
            np.int32) + self.label_offset
        
        if len(self.labels):
            string_labels = list()
            for label in labels:
                try:
                    string_labels.append(self.labels[int(label)])
                except IndexError:
                    raise NonMatchingIndexException(label)
            labels = string_labels
        return boxes, labels, scores
    
    def process_pose(self, annotation):
        """
        Parses the annotation to get the euler angles.

        Parameters
        ----------
            annotation: dict
                .. code-block:: python

                        {
                            "angles": [[roll, pitch, yaw]]
                        }                         

        Returns
        -------
            angles: list
                [roll, pitch, yaw]

        Raises
        ------
            None
        """
        return annotation.get("angles")[0]
    
    def process_segmentation(self, annotation):
        """
        Parses the annotations to get the segments and create the \
            detection mask.

        Parameters
        ----------
            annotation: dict

                .. code-block:: python
                        
                        {
                            "dimension": [height, width],
                            "segment": [[[x, y], [x,y], ...], [...]] 
                            "labels": [int, int, int ...] 
                        }
        
        Returns
        -------
            dt_mask: np.ndarray
                This is the same resolution as the image with 
                container integers per element depending on the label to
                represent each pixel. 
        
        Raises
        ------
            None
        """
        height, width = annotation.get("dimension")
        dt_mask = np.zeros((height, width))
        try:
            segments = []
            for polygon in annotation.get("segment"):
                # a list of vertices
                x_y = []
                for vertex in polygon:
                    vertex = self.denormalizer(
                        vertex, height, width) if \
                        self.denormalizer else vertex
                    x_y.append(float(vertex[0]))
                    x_y.append(float(vertex[1]))
                segments.append(x_y)
        except KeyError:
            return dt_mask
        try:
            offset = 1 
            labels = np.array(annotation["labels"]).astype(np.int32)
            labels += offset
        except KeyError:
            return dt_mask
        
        dt_instance = {
                "segments": segments,
                "labels": labels
        }
        return create_mask_image(height, width, dt_instance)