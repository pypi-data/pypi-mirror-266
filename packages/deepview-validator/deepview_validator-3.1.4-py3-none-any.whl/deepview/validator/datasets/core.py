# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import UnsupportedAnnotationFormatException
from deepview.validator.exceptions import UnsupportedDatasetTypeException
from deepview.validator.exceptions import InvalidDatasetSourceException
from deepview.validator.exceptions import DatasetNotFoundException
from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.exceptions import EmptyDatasetException
from deepview.validator.writers import Writer
from glob import glob
from PIL import Image
import numpy as np
import os

class Dataset:
    """
    Contains transformation methods for both images and annotations.
    Images can be resized and annotations can be normalized or denormalized. 
    Annotations can be converted to specific formats (yolo, coco, pascalvoc). 
    More information can be found on the annotation formats: \
        https://support.deepviewml.com/hc/en-us/articles/ \
            10869801702029-Darknet-Ground-Truth-Annotations-Schema

    Parameters
    ----------
        source: str
            The path to the source dataset.

        gformat: str
            The annotation format (yolo, pascalvoc, coco).

        absolute: bool
            If true, then the annotations are not normalized.

        validate_type: str
            Can be either 'detection', 'segmentation' or 'pose'.

        show_missing_annotations: bool
            If this is True, then print on the terminal
            all the file names with missing annotations. 
            Else, it will only print the number of missing annotations.

    Raises
    ------
        UnsupportedAnnotationFormatException
            Raised if the provided annotation format is not identified.

        UnsupportedDatasetTypeException
            Raised if the provided path does not reflect 
            either Darknet or TFRecord
            format.

        InvalidDatasetSourceException
            Raised if the path to the dataset is None.

        DatasetNotFoundException
            Raised if the provided path to the dataset does not exist.

        EmptyDatasetException
            Raised if the provided path to a directory does not 
            contain any images, text files, or tfrecord files.

        ValueError
            Raised if the provided path to the dataset is not a string. 
            Other raises are caused if the provided parameters
            in certain methods does not conform to the specified data type
            or the parameters are invalid. i.e. The image dimensions
            provided less than or equal to 0.
    """
    def __init__(
        self,
        source=None,
        gformat='yolo',
        absolute=False,
        validate_type='detection',
        show_missing_annotations=False
    ):
        self.source = source
        self.shape = None  # (height, width)
        self.format = gformat.lower()
        self.show_missing_annotations = show_missing_annotations
        self.absolute = absolute
        self.validate_type = validate_type

        if self.format not in ['yolo', 'pascalvoc', 'coco']:
            raise UnsupportedAnnotationFormatException(self.format)

        self.images, self.annotations = list(), list()

        self.transformer = None
        if self.format == 'yolo':
            self.transformer = self.yolo2xyxy
        elif self.format == 'coco':
            self.transformer = self.xywh2xyxy
        else:
            self.transformer = None

        self.normalizer = None
        self.denormalizer = None
        if absolute:
            if validate_type.lower() == 'detection':
                self.normalizer = self.normalize
        else:
            if validate_type.lower() == 'segmentation':
                self.denormalizer = self.denormalize_polygon

    @staticmethod
    def clamp_dim(dim1, dim2, min):
        """
        Clamps the bounding box dimensions to the minimum width or height set.

        Parameters
        ----------
            dim1: float
                xmin or ymin.

            dim2: float
                xmax or ymax.

            min: int
                The minimum acceptable dimension of the bounding box.

        Returns
        -------
            dim1, dim2: float
                This is the clamped dimensions.

        Raises
        ------
            None
        """
        return (dim1, dim1+min) if dim2-dim1 < min else (dim1, dim2)

    @staticmethod
    def validate_input_source(source):
        """
        Validates the existance of the source path.

        Parameters
        ----------
            source: str
                The path to the dataset.

        Returns
        -------
            source: str
                The validated path to the dataset.

        Raises
        ------
            InvalidDatasetSourceException
                Raised if the source to the dataset is None.

            DatasetNotFoundException
                Raised if the provided source to the dataset does not exist.

            ValueError
                Raised if the provided source to the dataset is not a string.
        """
        if source is None:
            raise InvalidDatasetSourceException(source)
        else:
            if not (isinstance(source, str)):
                raise ValueError(
                    "The provided path to the dataset is not a string. " +
                    "Recieved type: {}".format(
                        type(source)))
            if not os.path.exists(source):
                raise DatasetNotFoundException(source)
            else:
                return source
    
    @staticmethod
    def read_yaml_file(file_path):
        """
        Reads yaml files internal to AuZone for collecting
        dataset information.

        Parameters
        ----------
            file_path: str
                The path to the yaml file.

        Returns
        -------
            info_dataset: dict
                This contains the yaml file contents.
                
        Raises
        ------
            MissingLibraryException
                Raised if the yaml library is not installed in the system.
                
            FileNotFoundError
                Raised if the provided path to the file does not exist.
        """
        try:
            import yaml
        except ImportError:
            raise MissingLibraryException("The yaml library is needed to " +
                                          "read yaml files.")
        if os.path.exists(file_path):
            with open(file_path) as file:
                return yaml.full_load(file)
        else:
            raise FileNotFoundError("The yaml file is not found at: {}".format(
                file_path))

    def get_detection_dataset(self, source, labels_path=None):
        """
        Inspects the \*.yaml file contents if it exists.
        Otherwise it will search for either images with text
        annotations (Darknet) or tfrecord files (TFRecord Dataset).

        Parameters
        ----------
            source: str
                The validated path to the dataset.
                This can point to a yaml file or a directory containing
                tfrecords or images and text annotations.

            labels_path: str
                The path to the labels.txt (if provided).

        Returns
        -------
            dataset object: DarknetDataset or TFRecordDataset
                Depending on the dataset passed, the appropriate
                object will be created.

        Raises
        ------
            UnsupportedDatasetTypeException
                Raised if the yaml file specifies a dataset type that 
                is not recognized. Can only recognize (darknet or tfrecord).

            FileNotFoundError
                Raised if the provided path to the labels.txt does not exist.

            EmptyDatasetException
                Raised if the path provided does not contain 
                any tfrecords, images, or text annotations.
        """
        source = self.validate_input_source(source)

        if os.path.isdir(source):
            # Handle AuZoneNet and AuZoneTFRecords format.
            # Check if a dataset yaml file is inside the directory.
            for root, _, files in os.walk(source):
                for file in files:
                    if os.path.splitext(file)[1] == ".yaml":
                        return self.read_yaml_file(os.path.join(root, file))
            # Check if the labels file is inside the directory.
            labels_file = "labels.txt"
            labels = list()
            # Check if labels.txt is under /dataset_path (source)/labels.txt.
            if os.path.exists(os.path.join(source, labels_file)):
                labels_path = os.path.join(source, labels_file)
            # Check if labels.txt path is explicitly provided.
            elif labels_path is not None:
                labels_path = self.validate_input_source(labels_path)
            # If labels.txt is not found, then search through the dataset.
            else:
                for root, _, files in os.walk(source):
                    if labels_file in files:
                        labels_path = os.path.join(root, labels_file)
                # Continue validation without the label file.
                if labels_path is None:  
                    Writer.logger(
                        "The file labels.txt could not be found.", 
                        code="WARNING")
                
            if labels_path is not None:
                with open(labels_path) as file:
                    labels = [line.rstrip().lower()
                            for line in file.readlines() if line not in 
                                ["\n", "", "\t"]]
                    
            # Handles standard TFRecord datasets.
            info_dataset = dict()
            tfrecord_files = glob(os.path.join(source, "*.tfrecord"))
            if len(tfrecord_files) != 0:
                info_dataset["classes"] = labels
                info_dataset["validation"] = { "path": source }
                return info_dataset

            # Handles standard Darknet datasets.
            image_files = list()
            for extension in ['jpg', 'png', 'jpeg', 'JPG', 'PNG', 'JPEG']:
                if len(image_files) == 0:
                    image_files = glob(
                        os.path.join(source, f"*.{extension}"))
                    image_source = source
                    if len(image_files) == 0:
                        image_files = glob(os.path.join(
                            source, f"images/validate/*.{extension}"))
                        image_source = os.path.join(
                            source, "images/validate")
                else:
                    for ext in ['*.txt', '*.json']:
                        annotation_files = glob(os.path.join(source, ext))
                        annotation_source = source
                        if len(annotation_files) == 0 or (
                            len(annotation_files) == 1 and os.path.basename(
                                annotation_files[0]) == "labels.txt"):
                            annotation_files = glob(os.path.join(
                                source, 'labels/validate/'+ ext))
                            annotation_source = os.path.join(
                                source, "labels/validate")
                            if len(annotation_files) == 0:
                                continue
                            else:
                                break
                        else:
                            break
                    
                    if len(annotation_files) == 0:
                        raise EmptyDatasetException("annotations", source)

                    info_dataset["type"] = "darknet"
                    info_dataset["classes"] = labels
                    info_dataset["validation"] = {
                        "images": image_source,
                        "annotations": annotation_source
                    }
                    return info_dataset
                    
        elif os.path.isfile(source):
            if os.path.splitext(os.path.basename(source))[1] == ".yaml":
                return self.read_yaml_file(source)
            elif os.path.splitext(os.path.basename(source))[1] == ".txt":
                raise NotImplementedError(
                    "Single text file is not currently supported.")
            elif os.path.splitext(source)[1] == ".deepview":
                raise NotImplementedError(
                    "Deepview files are not currently supported.")
            else:
                UnsupportedDatasetTypeException(source)
        else:
            UnsupportedDatasetTypeException(source)

    def check_labels_type(self, labels):
        """
        This method handles type of labels wether it is a numpy array or a \
            standard python list or if the contents are integers or strings. 
            For these cases, this method converts the labels into a list of \
                strings in validation.
        
        Parameters
        ----------
            labels: list or np.ndarray
                This is the labels for the ground truth annotation on a single
                image.

        Returns
        -------
            labels: list
                A list on containing string representations.

        Raises
        ------
            ValueError
                Raised if the passed labels is neither a list nor np.ndarray. 
                Raised if the contents inside labels is neither an integer
                or a string.
        """
        if isinstance(labels, np.ndarray):
            if labels.dtype in ["int32", "int64"]:
                labels = \
                    [self.labels[int(label)].lower() for label in labels]
            elif labels.dtype.type is not np.str_:
                raise ValueError("All elements in the labels numpy array " +
                                "must either be int or strings.")
        elif isinstance(labels, list):
            if all(isinstance(label, int) for label in labels):
                labels = \
                    [self.labels[label].lower() for label in labels]
            elif not all(isinstance(label, str) for label in labels):
                raise ValueError("All elements in the labels list " +
                                "must either be strings or integers.")
        else:
            raise ValueError("labels can only be of type list or np.ndarray.")
        return labels

    @staticmethod
    def validate_dimension(dimension):
        """
        Checks that image or frame dimensions are integers. 
        Dimensions cannot be less than or equal to 0.

        Parameters
        ----------
            dimension: int
                The dimension to validate.

        Returns
        -------
            dimension: int
                The validated dimension that is an integer
                and is greater than 0.

        Raises
        ------
            ValueError
                Raised if the dimension is not an integer 
                or it is less than or equal to 0.
        """
        if not (isinstance(dimension, int)):
            raise ValueError("The provided dimension is not an integer. " +
                             "Recieved type: {}".format(type(dimension)))
        elif (dimension <= 0):
            raise ValueError("The provided dimension is invalid. " +
                             "Recieved dimension: {}".format(dimension))
        else:
            return dimension

    @staticmethod
    def resize(image, size=None):
        """
        Resizes the images depending on the size passed.

        Parameters
        ----------
            image: (height, width, 3) np.ndarray
                The image represented as a numpy array.

            size: (height, width) tuple
                Specify the size to resize.

        Returns
        -------
            image: (height, width, 3)
                Resized image.

        Raises
        ------
            ValueError
                Raised if the provided image is not a 
                np.ndarray or the given string image path does not exist.
        """
        if size is None:
            return image
        else:
            # Resize method requires (width, height)
            size = (size[1], size[0])
            if isinstance(image, str):
                if os.path.exists(image):
                    image = Image.open(image)
                    image = image.resize(size)
                    return np.asarray(image)
                else:
                    raise ValueError(
                        "The given image path does not exist at {}".format(
                            image)
                    )
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(np.uint8(image))
                image = image.resize(size)
                return np.asarray(image)
            else:
                raise ValueError(
                    "The image provided is neither a " +
                    "numpy array or a pillow image object. " +
                    "Recieved type: {}".format(type(image)))
            
    @staticmethod
    def bgr2rgb(image):
        """
        Converts BGR image to RGB image.

        Parameters
        ----------
            image: (height, width, 3) np.ndarray
                The image as a BGR numpy array.

        Returns
        -------
            image: (height, width, 3) np.ndarray
                The image as a RGB image.

        Raises
        ------
            NotImplementedError
                This method is currently not implemented.
        """
        raise NotImplementedError("This method is currently not implemented.")

    @staticmethod
    def rgb2bgr(image):
        """
        This method converts RGB image to BGR image.
    
        Parameters
        ----------
            image: (height, width, 3) np.ndarray
                The image as a RGB numpy array.

        Returns
        -------
            image: (height, width, 3) np.ndarray
                The image as a BGR image.

        Raises
        ------
            NotImplementedError
                This method is currently not implemented.
        """
        raise NotImplementedError("This method is currently not implemented.")

    @staticmethod
    def normalize(boxes, height, width):
        """
        Normalizes the boxes to the width and height of the 
        image or model input resolution.

        Parameters
        ----------
            boxes: np.ndarray
                List of lists of floats [[boxes1], [boxes2]].
                Contains boxes to normalize.

            height: int
                The dimension to normalize the y-coordinates.

            width: int
                The dimension to normalize the x-coordinates.

        Returns
        -------
            Normalized boxes: np.ndarray
                new x-coordinate = old x-coordinate/width
                new y-coordinate = old y-coordinate/height

        Raises
        ------
            ValueError
                Raised if the provided boxes is not a numpy array or 
                if the provided height and width are not integers 
                or they have invalid dimensions 
                which are less than or equal to 0.
        """
        if not (isinstance(boxes, np.ndarray)):
            raise ValueError("The provided boxes is not a numpy array. " +
                             "Recieved type: {}".format(boxes))
        else:
            if not (isinstance(height, int) or isinstance(width, int)):
                raise ValueError(
                    "The provided width or height is not an integer. " +
                    "Recieved width: {} and height: {}".format(
                        type(width),
                        type(height)))
            elif (height <= 0 or width <= 0):
                raise ValueError(
                    "The provided width and height has invalid dimensions. " +
                    "Recieved width: {} and height: {}".format(
                        width,
                        height))
            else:
                boxes[..., 0:1] /= width
                boxes[..., 1:2] /= height
                boxes[..., 2:3] /= width
                boxes[..., 3:4] /= height
                return boxes

    @staticmethod
    def denormalize(boxes, height, width):
        """
        Denormalizes the boxes by the width and height of the image 
        or model input resolution to get the pixel values of the boxes.
    
        Parameters
        ----------
            boxes: np.ndarray
                List of lists of floats [[boxes1], [boxes2]].
                Contains boxes to denormalize.

            height: int
                The dimension to denormalize the y-coordinates.

            width: int
                The dimension to denormalize the x-coordinates.

        Returns
        -------
            Denormalized boxes: np.ndarray
                new x-coordinate = old x-coordinate*width
                new y-coordinate = old y-coordinate*height

        Raises
        ------
            ValueError
                Raised if the provided boxes is not a numpy array or 
                if the provided height and width are not integers 
                or they have invalid dimensions which are less
                than or equal to 0.
        """
        if not (isinstance(boxes, (list, np.ndarray))):
            raise ValueError("The provided boxes is not a numpy array. " +
                             "Recieved type: {}".format(boxes))
        else:
            if not (isinstance(height, int) or isinstance(width, int)):
                raise ValueError(
                    "The provided width or height is not an integer. " +
                    "Recieved width: {} and height: {}".format(type(width),
                                                               type(height)))
            elif (height <= 0 or width <= 0):
                raise ValueError(
                    "The provided width and height has invalid dimensions. " +
                    "Recieved width: {} and height: {}".format(width, height))
            else:
                if isinstance(boxes, list):
                    boxes = np.array(boxes)
                boxes[..., 0:1] *= width
                boxes[..., 1:2] *= height
                boxes[..., 2:3] *= width
                boxes[..., 3:4] *= height
                return boxes.astype(np.int32)

    @staticmethod
    def normalize_polygon(vertex, height, width):
        """
        Normalizes the vertex coordinate of a polygon.

        Parameters
        ----------
            vertex: list
                This contains [x, y] coordinate.

            height: int
                The dimension to normalize the y-coordinates.

            width: int
                The dimension to normalize the x-coordinates.

        Returns
        -------
            normalized coordinates: list
                This contains [x, y].

        Raises
        ------
            ValueError
                Raised if the provided height and width are 
                not integers or they have invalid dimensions 
                which are less than or equal to 0.
        """
        if not (isinstance(height, int) or isinstance(width, int)):
            raise ValueError(
                "The provided width or height is not an integer. " +
                "Recieved width: {} and height: {}".format(
                    type(width),
                    type(height)))
        elif (height <= 0 or width <= 0):
            raise ValueError(
                "The provided width and height has invalid dimensions. " +
                "Recieved width: {} and height: {}".format(
                    width,
                    height))
        else:
            return [float(vertex[0]) / width, float(vertex[1]) / height]

    @staticmethod
    def denormalize_polygon(vertex, height, width):
        """
        Denormalizes the vertex coordinate of a polygon.

        Parameters
        ----------
            vertex: list
                This contains [x, y] coordinate.

            height: int
                The dimension to denormalize the y-coordinates.

            width: int
                The dimension to denormalize the x-coordinates.

        Returns
        -------
            Denormalized coordinates: list
                This contains [x, y].

        Raises
        ------
            ValueError
                Raised if the provided height and width are 
                not integers or they have invalid dimensions 
                which are less than or equal to 0.
        """
        if not (isinstance(height, int) or isinstance(width, int)):
            raise ValueError(
                "The provided width or height is not an integer. " +
                "Recieved width: {} and height: {}".format(
                    type(width),
                    type(height)))
        elif (height <= 0 or width <= 0):
            raise ValueError(
                "The provided width and height has invalid dimensions. " +
                "Recieved width: {} and height: {}".format(
                    width,
                    height))
        else:
            return [
                int(float(vertex[0]) * width), int(float(vertex[1]) * height)]

    @staticmethod
    def yolo2xyxy(boxes):
        """
        Converts yolo format into pascalvoc format.

        Parameters
        ----------
            boxes: np.ndarray
                Contains lists for each boxes in
                yolo format [[boxes1], [boxes2]].

        Returns
        -------
            boxes: np.ndarray
                Contains list for each boxes in
                pascalvoc format.

        Raises
        ------
            ValueError
                Raised if the provided boxes 
                parameter is not a numpy array.
        """
        if not (isinstance(boxes, np.ndarray)):
            raise ValueError(
                "The parameter for boxes has an incorrect type. " +
                "Requires numpy array but recieved {}".format(
                    type(boxes)))
        else:
            w_c = boxes[..., 2:3]
            h_c = boxes[..., 3:4]
            boxes[..., 0:1] = boxes[..., 0:1] - w_c / 2
            boxes[..., 1:2] = boxes[..., 1:2] - h_c / 2
            boxes[..., 2:3] = boxes[..., 0:1] + w_c
            boxes[..., 3:4] = boxes[..., 1:2] + h_c
            return boxes

    @staticmethod
    def xywh2xyxy(boxes):
        """
        Converts coco format to pascalvoc format.

        Parameters
        ----------
            boxes: np.ndarray
                Contains lists for each boxes in
                coco format [[boxes1], [boxes2]].

        Returns
        -------
            boxes: np.ndarray
                Contains list for each boxes in
                pascalvoc format.

        Raises
        ------
            ValueError
                Raised if the provided boxes parameter 
                is not a numpy array.
        """
        if not (isinstance(boxes, np.ndarray)):
            raise ValueError(
                "The parameter for boxes has an incorrect type. " +
                "Requires numpy array but recieved {}".format(
                    type(boxes)))
        else:
            boxes[..., 2:3] = boxes[..., 2:3] + boxes[..., 0:1]
            boxes[..., 3:4] = boxes[..., 3:4] + boxes[..., 1:2]
            return boxes

    def build_dataset(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method.")

    def read_sample(self, instance):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method.")

    def read_all_samples(self, info="Validation Progress"):
        """
        Reads all the samples in either Darknet or TFRecord datasets.

        Parameters
        ----------
            info: str
                The description of why image instances are being read.
                By default it is to run validation, 
                hence "Validation Progress".

        Returns
        -------
            ground truth instance: dict
                Yeilds one sample of the ground truth
                instance which contains information on the image
                as a numpy array, boxes, labels, and image path.

        Raises
        ------
            None
        """
        try:
            from tqdm import tqdm
        except ImportError:
            pass

        try:
            instances = tqdm(self.build_dataset(), colour="green")
            instances.set_description(info)
            for instance in instances:
                yield self.read_sample(instance)
        except NameError:
            instances = self.build_dataset()
            num_samples = len(instances)
            for index in range(num_samples):
                print(
                    "\t - [INFO]: Computing Metrics for instance: " +
                    "%i of %i [%2.f %s]" %
                    (index + 1,
                     num_samples,
                     100 * ((index + 1) / float(num_samples)),
                     '%'), end='\r')
                yield self.read_sample(instances[index])
