# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import sys

class DivisionByZeroException(Exception):
    """
    This exception will be raised when
    a division by zero occurs.

    Parameters
    ----------
        computation_type: str
            Which computation resulted in the error? Ex. precision, recall ...

        numerator: float or int
            Value to be divided.

        denominator: float or int
            Value that divides in this case, 0.
    """

    def __init__(self, computation_type, numerator, denominator):
        sys.tracebacklimit = 0
        super(
            DivisionByZeroException,
            self).__init__(
            "When calculating {}, could not perform".format(computation_type) +
            " division by zero operation: {}/{}".format(
                numerator,
                denominator))

class ZeroUniqueLabelsException(Exception):
    """
    This exception will be raised when
    the number of unique labels in the dataset is zero.
    """

    def __init__(self):
        sys.tracebacklimit = 0
        super(ZeroUniqueLabelsException, self).__init__(
            "The number of unique classes returned zero. " +
            "Check if the path to the dataset is correct.")

class UnsupportedAnnotationFormatException(Exception):
    """
    This exception will be raised when
    the annotation format is not accepted.

    Parameters
    ----------
        annotation_format: str
            The format of the annotations (yolo, pascalvoc, coco).
    """

    def __init__(self, annotation_format):
        sys.tracebacklimit = 0
        super(
            UnsupportedAnnotationFormatException,
            self).__init__(
            "The annotation format {} ".format(annotation_format) +
            "is not supported. Can only support 'yolo', 'pascalvoc', 'coco'.")

class UnsupportedAnnotationExtensionException(Exception):
    """
    This exception will be raised when
    the annotation extension passed is not supported.

    Parameters
    ----------
        extension: str
            The annotation extension.
    """

    def __init__(self, extension):
        sys.tracebacklimit = 0
        super(
            UnsupportedAnnotationExtensionException,
            self).__init__(
            "The given annotation extension {} ".format(extension) +
            "is currently not supported. Can only accept 'txt' or 'json'.")

class UnsupportedImageExtensionException(Exception):
    """
    This exception will be raised when
    the image extension passed is not supported.

    Parameters
    ----------
        extension: str
            The image extension.
    """

    def __init__(self, extension):
        sys.tracebacklimit = 0
        super(UnsupportedAnnotationExtensionException, self).__init__(
            "The given image extension {} is currently not supported.".format(
                extension))

class UnsupportedDatasetTypeException(Exception):
    """
    This exception will be raised when
    the given dataset type is not supported.

    Parameters
    ----------
        dataset_type: str
            The type of the dataset.
    """

    def __init__(self, dataset_type):
        sys.tracebacklimit = 0
        super(
            UnsupportedDatasetTypeException,
            self).__init__(
            "The given dataset type {} is currently ".format(dataset_type) +
            "not supported. Can only support Darknet and TFRecord Datasets.")

class LabelsFileNotFoundException(Exception):
    """
    This exception will be raised when
    the labels file could not be located.

    Parameters
    ----------
        labels_file: str
            The path to the labels_file.
    """

    def __init__(self, labels_file):
        sys.tracebacklimit = 0
        super(LabelsFileNotFoundException, self).__init__(
            "Could not locate labels.txt at {}".format(labels_file))

class EmptyDatasetException(Exception):
    """
    This exception will be raised when
    the dataset provided is empty.

    Parameters
    ----------
        info: str
            The dataset portion that is empty (annotations or images)

        source: str
            The path to the dataset portion that fails.
    """

    def __init__(self, info, source):
        sys.tracebacklimit = 0
        super(EmptyDatasetException, self).__init__(
            "The are no {} at {}.".format(info, source))

class DatasetNotFoundException(Exception):
    """
    This exception will be raised when
    the pass path to the dataset does not exist.

    Parameters
    ----------
        source: str
            The path to the dataset.
    """

    def __init__(self, source):
        sys.tracebacklimit = 0
        super(DatasetNotFoundException, self).__init__(
            "The given dataset path does not exist at: {}.".format(source))

class InvalidDatasetSourceException(Exception):
    """
    This exception will be raised when
    the passed path to the dataset is None.

    Parameters
    ----------
        source: str
            The path to the dataset.
    """

    def __init__(self, source):
        sys.tracebacklimit = 0
        super(InvalidDatasetSourceException, self).__init__(
            "The given dataset path returned {}.".format(source))

class InvalidModelSourceException(Exception):
    """
    This exception will be raised when
    the passed path to the model is None.

    Parameters
    ----------
        source: str
            The path to the model.

    """

    def __init__(self, source):
        sys.tracebacklimit = 0
        super(InvalidDatasetSourceException, self).__init__(
            "The given model path returned {}.".format(source))

class UnsupportedModelExtensionException(Exception):
    """
    This exception will be raised when
    the passed model has a type that is currently
    not supported.

    Parameters
    ----------
        model_extension: str
            The extension of the model.
    """

    def __init__(self, model_extension):
        sys.tracebacklimit = 0
        super(
            UnsupportedModelExtensionException,
            self).__init__(
            "The given model extension {} is currently not supported. ".format(
            model_extension) + "Can only support .rtm, .h5, or .tflite")

class UnsupportedModelTypeException(Exception):
    """
    This exception will be raised when
    the passed model has a type that is currently
    not supported.

    Parameters
    ----------
        model_type: str
            The type of the model.
    """

    def __init__(self, model_type):
        sys.tracebacklimit = 0
        super(
            UnsupportedModelTypeException,
            self).__init__(
            "The given model type {} is currently ".format(model_type) +
            "not supported. Can only support 'modelpack' or 'yolo'.")

class UnsupportedEngineException(Exception):
    """
    This exception will be raised when
    the given engine type is not supported.

    Parameters
    ----------
        engine: str
            The type of engine (npu, cpu, gpu).
    """

    def __init__(self, engine):
        sys.tracebacklimit = 0
        super(UnsupportedEngineException, self).__init__(
            "The given engine type {} is not supported. ".format(engine) +
            "Can only support 'npu', 'cpu', 'gpu'.")

class UnsupportedNMSException(Exception):
    """
    This exception will be raised when
    the given NMS type is not supported.

    Parameters
    ----------
        nms: str
            The type of NMS to perform.
    """

    def __init__(self, nms):
        sys.tracebacklimit = 0
        super(UnsupportedNMSException, self).__init__(
            "The given NMS {} is not supported. ".format(nms) +
            "Can only support 'fast', 'standard', 'matrix'.")

class UnsupportedNormalizationException(Exception):
    """
    This exception will be raised when
    the given normalization is not supported.

    Parameters
    ----------
        norm: str
            The type of image normalization.
    """

    def __init__(self, norm):
        sys.tracebacklimit = 0
        super(UnsupportedNormalizationException, self).__init__(
            "The given normalization {} is not supported. ".format(norm) +
            "Can only support 'raw', 'signed', 'unsigned'.")

class ModelUnknownLabelsException(Exception):
    """
    This exception will be raised if
    the model that was given has no labels.

    Parameters
    ----------
        model: str
            The path to the model.
    """

    def __init__(self, model):
        sys.tracebacklimit = 0
        super(ModelUnknownLabelsException, self).__init__(
            "The given model {} does not output any labels.".format(model))

class NonMatchingIndexException(Exception):
    """
    This exception will be raised if
    the index of the unique label
    list is out of bounds.

    Parameters
    ----------
        index: str
            The index that is out of bounds.

        cause: str
            The cause of the issue. By default it is during prediction.
    """

    def __init__(self, index, cause="prediction"):
        sys.tracebacklimit = 0
        super(NonMatchingIndexException, self).__init__(
            "The given {} index {} is out of bounds ".format(cause, index) +
            "to the unique label list.")

class MatchingAlgorithmException(Exception):
    """
    This exception will be raised if
    the matching algorithm encountered
    invalid values for both IoU
    and ground truth index.
    """

    def __init__(self, message):
        sys.tracebacklimit = 0
        super(
            MatchingAlgorithmException,
            self).__init__(message)

class InvalidIoUException(Exception):
    """
    This exception will be raised if
    the IoU value is invalid such as
    less than 0 or greater than 1.

    Parameters
    ----------
        iou: float
            The intersection over union score.
    """

    def __init__(self, iou):
        sys.tracebacklimit = 0
        super(InvalidIoUException, self).__init__(
            "The IoU value {} is invalid.".format(iou))

class ModelRunnerFailedConnectionException(Exception):
    """
    This exception will be raised if
    connecting to modelrunner fails.

    Parameters
    ----------
        target: str
            The modelrunner target. Ex: 10.10.40.205:10817
    """

    def __init__(self, target):
        sys.tracebacklimit = 0
        super(ModelRunnerFailedConnectionException, self).__init__(
            "Could not connect to modelrunner " +
            "with the target, {}".format(target))

class UnsupportedApplicationException(Exception):
    """
    This exception will be raised if
    the provided validation application
    is not supported.

    Parameters
    ----------
        application: str
            The application that is passed.
    """

    def __init__(self, application):
        sys.tracebacklimit = 0
        super(UnsupportedApplicationException, self).__init__(
            "Could not recognize the application, {}. ".format(application) +
            "Can only accept 'vaal' or 'modelclient'.")

class UnsupportedValidationTypeException(Exception):
    """
    This exception will be raised if
    the provided validation type
    is not supported.

    Parameters
    ----------
        validation_type: str
            The type of validation to perform.
    """

    def __init__(self, validation_type):
        sys.tracebacklimit = 0
        super(
            UnsupportedValidationTypeException,
            self).__init__(
            "Could not recognize the type of validation, {}. ".format(
                validation_type
            ) + "Can only support 'detection' or 'segmentation'.")

class MissingLibraryException(Exception):
    """
    This exception will be raised if
    the import of a library is fails
    which could mean that the user
    needs to install the library.

    Parameters
    ----------
        message: str
            This explains why the exception was raised.
    """

    def __init__(self, message):
        sys.tracebacklimit = 0
        super(MissingLibraryException, self).__init__(
            "Missing library: {}".format(message))