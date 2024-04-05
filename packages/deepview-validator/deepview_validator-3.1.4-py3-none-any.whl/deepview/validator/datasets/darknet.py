# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import EmptyDatasetException
from os.path import join, exists, basename, splitext
from deepview.validator.datasets.core import Dataset
from deepview.validator.writers import Writer
from glob import glob
from PIL import Image, ImageFile

import numpy as np
import warnings

class DarkNetDataset(Dataset):
    """
    Reads Darknet format datasets.
    Dataset format should be the same as coco128 at \
        https://www.kaggle.com/datasets/ultralytics/coco128.
    Optionally, the images and text annotations can be in the same directory.

    Parameters
    ----------
        source: str
            The path to the source dataset.

        info_dataset: dict
            Contains information such as:

                .. code-block:: python

                    {
                        "classes": [list of unique labels],
                        "validation":
                        {
                            "images: 'path to the images',
                            "annotations": 'path to the annotations'
                        }
                    }

            *Note: the classes are optional and the path to the images
            and annotations can be the same.*

        gformat: str
            The annotation format that can be either 'yolo', 'pascalvoc',
            or 'coco'. By default darknet datasets have annotations in
            'yolo' format.

        absolute: bool
            Specify as True if the annotations are not normalized to the
            image dimensions. By default they are normalized.

        validate_type: str
            The type of validation to perform that can be 'detection' or
            'segmentation'.

        show_missing_annotations: bool
            If this is True, then print on the terminal all
            missing annotations. Else, it will only
            print the number of missing annotations.

    Raises
    ------
        InvalidDatasetSourceException
            Raised if the path to the images or annotations is None.

        DatasetNotFoundException
            Raised if the provided path to the images or 
            annotations does not exist.

        ValueError
            Raised if the provided path to the images or 
            annotations is not a string.

        EmptyDatasetException
            Raised if the provided path to the images or 
            text files does not contain any image files or 
            text files respectively.
    """
    def __init__(
        self,
        source,
        info_dataset=None,
        gformat='yolo',
        absolute=False,
        validate_type="detection",
        show_missing_annotations=False
    ):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        
        super(DarkNetDataset, self).__init__(
            source=source,
            gformat=gformat,
            absolute=absolute,
            validate_type=validate_type,
            show_missing_annotations=show_missing_annotations
        )

        if info_dataset is None:
            info_dataset = self.get_detection_dataset(source)

        self.validate_type = validate_type.lower()
        self.image_source = self.validate_input_source(
            info_dataset.get('validation').get('images'))
        self.annotation_source = self.validate_input_source(
            info_dataset.get('validation').get('annotations'))
        self.labels = info_dataset.get('classes', None)

        self.images = list()
        for ext in ['*.[pP][nN][gG]', '*.[jJ][pP][gG]', '*.[jJ][pP][eE][gG]']:
            partial = glob(join(self.image_source, ext))
            self.images = self.images + partial
        
        self.images = sorted(self.images)
        
        if len(self.images) == 0:
            raise EmptyDatasetException(
                "images",
                self.image_source
            )

        for ext in ['*.txt', '*.json']:
            self.annotations = glob(join(self.annotation_source, ext))
            if len(self.annotations) == 0 or (
                len(self.annotations) == 1 and basename(
                    self.annotations[0]) == "labels.txt"):
                continue
            else:
                break
        
        if len(self.annotations) == 0:
            raise EmptyDatasetException(
                "annotations",
                self.annotation_source
            )

        self.annotation_extension = splitext(
            self.annotations[0]
        )[1]

    def build_dataset(self):
        """
        Builds the instances to allow iteration in the dataset.

        Parameters
        ----------
            None

        Returns
        -------
            instances: list of tuples
                One instance contains the
                (path to the image, path to the annotation).

        Raises
        ------
            None
        """
        missing_annotations = 0
        instances = list()
        for image_path in self.images:
            annotation_path = join(
                self.annotation_source,
                splitext(
                    basename(image_path))[0] +
                self.annotation_extension)
            
            if exists(annotation_path):
                instances.append((image_path, annotation_path))
            else:
                instances.append((image_path, None))
                if self.show_missing_annotations:
                    Writer.logger(
                        "Could not find the annotation " +
                        "for this image: {}. ".format(
                            basename(image_path)) +
                        "Looking for {}".format(
                            splitext(
                                basename(image_path))[0] +
                            self.annotation_extension),
                        code="WARNING")
                    missing_annotations += 1
                else:
                    missing_annotations += 1

        if not self.show_missing_annotations and missing_annotations > 0:
            Writer.logger(
                "There were {} images without annotations. ".format(
                    missing_annotations) + "To see the names of the images, " +
                "enable --show_missing_annotations in the command line.",
                code="WARNING")
        return instances

    def read_sample(self, instance):
        """
        Reads one sample from the dataset.
        
        Parameters
        ----------
            instance: tuple
                This contains (image path, annotation path).

        Returns
        -------
            ground truth instance: dict
                This contains information such as:

                    .. code-block:: python

                        {
                            'image': image numpy array,
                            'height': height,
                            'width': width,
                            'boxes': list bounding boxes,
                            'labels': list of labels,
                            'image_path': image_path
                        }

        Raises
        ------
            None
        """
        image_path, annotation_path = instance
        image = Image.open(image_path)

        if image.mode in ["RGB", "RGBA", "CMYK", "YCbCr"]:
            image = np.asarray(image)
        else:
            image.convert("RGB")
            image = np.asarray(image, dtype=np.uint8)
            image = np.stack((image,)*3, axis=-1)
            
        height, width, _ = image.shape

        if self.validate_type == 'detection':
            load = self.txt_load_boxes(annotation_path)
        elif self.validate_type == "segmentation":
            load = self.json_load_segments(annotation_path, height, width)
        elif self.validate_type == "pose":
            load = self.json_load_angles(annotation_path)
        else:
            raise ValueError("Invalid validation type: {}".format(
                self.validate_type))
        
        gt_instance = {
            "image": image,
            "height": height,
            "width": width,
            "image_path": image_path
            }
        gt_instance.update(load)
        return gt_instance

    def txt_load_boxes(self, annotation_path):
        """
        Reads from the text file annotation.

        Parameters
        ----------
            annotation_path: str
                This is the path to the text file annotation.

        Returns
        -------
            annotation info: dict
                This contains information such as:

                    .. code-block:: python

                        {
                            'boxes': list of bounding boxes,
                            'labels': list of labels
                        }

        Raises
        ------
            None
        """
        annotations = {
            "boxes": np.array([]),
            "labels": np.array([]).astype(np.int32)
        }

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                annotation = np.genfromtxt(annotation_path)
        except TypeError:
            return annotations

        if len(annotation):
            annotation = annotation.reshape(-1, 5)
            boxes = annotation[:, 1:5]
            boxes = self.normalizer(boxes) if self.normalizer else boxes
            boxes = self.transformer(boxes) if self.transformer else boxes
        else:
            return annotations

        labels = annotation[:, 0:1].flatten().astype(np.int32)
        if len(self.labels):
            labels = self.check_labels_type(labels)
           
        annotations["boxes"] = boxes
        annotations["labels"] = labels   
        return annotations

    def json_load_boxes(self, annotation_path):
        """
        Reads from the JSON annotation.

        Parameters
        ----------
            annotation_path: str
                This is the path to the JSON annotation.

        Returns
        -------
            annotation info: dict
                This contains information such as:

                    .. code-block:: python

                        {
                            'boxes': list of bounding boxes,
                            'labels': list of labels
                        }

        Raises
        ------
            None
        """
        import json
        annotations = {
                "boxes": np.array([]),
                "labels": np.array([]).astype(np.int32)
            }

        try:
            with open(annotation_path) as file:
                data = json.load(file)
                try:
                    annotation = np.array(data["boxes"])
                    annotation = self.normalizer(
                        annotation) if self.normalizer else annotation
                    boxes = self.transformer(
                        annotation[:, 0:5]
                    ) if self.transformer else annotation[:, 0:5]
                except KeyError:
                    return annotations
                try:
                    labels = data["labels"]
                    if len(self.labels):
                        labels = self.check_labels_type(labels)
                    else:
                        labels = data["labels"]
                except KeyError:
                    return annotations
        except (FileNotFoundError, TypeError):
            return annotations

        annotations["boxes"] = boxes
        annotations["labels"] = np.array(labels)
        return annotations
    
    def json_load_segments(self, annotation_path, height, width):
        """
        Loads a single instance from a JSON file in the image dataset 
        to grab the segments.

        Parameters
        ----------
            annotation_path: str
                This is the path to the JSON annotation.

            height: int
                This is the image height.
            
            width: int
                This is the image width.

        Returns
        -------
            annotation info: dict
                This contains information such as:

                    .. code-block:: python

                        {
                            'boxes': list of polygon segments,
                            'labels': list of labels
                        }

        Raises
        ------
            None
        """
        annotations = {
            "segments": np.array([]),
            "labels": np.array([]).astype(np.int32)
        }

        import json
        try:
            with open(annotation_path) as file:
                data = json.load(file)
                try:
                    segments = []
                    for polygon in data["segment"]:
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
                    return annotations
                try:
                    offset = 1 
                    labels = np.array(data["labels"]).astype(np.int32)
                    labels += offset
                except KeyError:
                    return annotations
        except (FileNotFoundError, TypeError):
            return annotations

        annotations["segments"] = segments
        annotations["labels"] = labels
        return annotations

    def json_load_angles(self, annotation_path):
        """
        Opens JSON file to parse the angles for headpose validation.

        Parameters
        ----------
            annotation_path: str
                The path to the annotation file.

        Returns
        -------
            load: dictionary
                This contains the angles and the labels.

                    .. code-block:: python

                        {
                            "angles": [roll, pitch, yaw],
                            "labels": [helmet]
                        }

        Raises
        ------
            None
        """
        import json
        annotations = {
            "boxes": np.array([[]]),
            "angles": np.array([[]]),
            "labels": np.array([]).astype(np.int32)
        }

        try:
            with open(annotation_path) as file:
                data = json.load(file)
                try:
                    angles = data.get("angles")
                    if data.get("boxes") is None:
                        raise TypeError(
                            "There are no boxes for this file {}".format(
                                basename(annotation_path)))
                    if len(data.get("boxes")):
                        labels = np.array(data.get("boxes"))[:, 4:5].astype(
                            np.int32)
                        if len(self.labels):
                            labels = self.check_labels_type(labels)
                        
                        boxes = np.array(data.get("boxes"))
                        boxes = boxes[:, 0:4]
                        boxes = self.normalizer(
                            boxes) if self.normalizer else boxes
                        boxes = self.transformer(
                            boxes) if self.transformer else boxes
                    else:
                        labels = list()
                        boxes = list()
                except KeyError:
                    return annotations
        except FileNotFoundError:
            return annotations
        
        annotations["angles"] = angles
        annotations["labels"] = labels
        annotations["boxes"] = boxes
        return annotations
    