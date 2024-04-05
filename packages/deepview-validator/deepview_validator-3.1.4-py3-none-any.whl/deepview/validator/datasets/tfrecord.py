# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.exceptions import EmptyDatasetException
from deepview.validator.datasets.core import Dataset
from os.path import join
from glob import glob
import numpy as np

class TFRecordDataset(Dataset):
    """
    Reads TFRecord Datasets.
    
    Parameters
    ----------
        source: str
            The path to the source dataset.

        info_dataset: dict
            Contains information such as:

                .. code-block:: python

                    {
                        "classes": [list of unique labels],
                        "validation": {
                            "path": path to the *.tfrecord files.
                        }
                    }

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

    Raises
    ------
        InvalidDatasetSourceException
            Raised if the path to the tfrecord files is None.

        DatasetNotFoundException
            Raised if the provided path to the tfrecord files does not exist.

        ValueError
            Raised if the provided path to the tfrecord files is not a string.

        EmptyDatasetException
            Raised if the provided path to the tfrecord files does not contain
            any tfrecord files.
    """
    def __init__(
        self,
        source,
        info_dataset=None,
        gformat='yolo',
        absolute=False,
        validate_type='detection'
    ):
        super(TFRecordDataset, self).__init__(
            source=source,
            gformat=gformat,
            absolute=absolute,
            validate_type=validate_type
        )

        if info_dataset is None:
            info_dataset = self.get_detection_dataset(source)

        self.source = self.validate_input_source(
            info_dataset.get('validation').get('path'))
        self.labels = info_dataset.get('classes', None)

        self.tfrecords = glob(join(self.source, '*.tfrecord'))
        if len(self.tfrecords) == 0:
            raise EmptyDatasetException("tfrecord files", self.source)

    def py_read_data(self, example):
        """
        This method reads the from the file to extract information.
        
        Parameters
        ----------
            example:

        Returns
        -------

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed in the system.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException("Tensorflow library is needed to " +
                                          "read tfrecord datasets.")

        feature_description = {
            "image": tf.io.FixedLenFeature([], tf.string),
            "image_name": tf.io.FixedLenFeature([], tf.string),
            "width": tf.io.FixedLenFeature([], tf.int64),
            "height": tf.io.FixedLenFeature([], tf.int64),
            "objects": tf.io.VarLenFeature(tf.int64),
            "bboxes": tf.io.VarLenFeature(tf.float32),
        }
        sample = tf.io.parse_single_example(
            example,
            feature_description)

        img = tf.io.decode_jpeg(sample['image']).numpy()
        height, width, _ = img.shape

        labels = tf.sparse.to_dense(sample['objects']).numpy().astype(np.int32)
        boxes = np.array([], dtype=np.float32)

        if len(labels):
            boxes = tf.sparse.to_dense(
                sample['bboxes']).numpy().reshape(-1, 4).astype(np.float32)
            boxes = self.normalizer(boxes) if self.normalizer else boxes
            boxes = self.transformer(boxes) if self.transformer else boxes
            boxes[boxes < 0] = 0.0
        return img, boxes, labels, height, width, sample.get('image_name')

    def read_data(self, path):
        """
        This method reads the tfrecord data.

        Parameters
        ----------
            path:

        Returns
        -------

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow is not installed in the system.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException("Tensorflow library is needed to " +
                                          "read tfrecord datasets.")

        return tf.py_function(
            self.py_read_data,
            [path],
            Tout=[tf.uint8, tf.float32, tf.int32,
                  tf.int32, tf.int32, tf.string])

    def build_dataset(self):
        """
        Builds the dataset. Records contain information for each image.

        Parameters
        ----------
            None

        Returns
        -------
            records:

        Raises
        ------
            MissingLibraryException
                Raised if tensorflow library is not installed in the system.
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException("Tensorflow library is needed to " +
                                          "read tfrecord datasets.")
        iter = tf.data.TFRecordDataset(
            self.tfrecords,
            num_parallel_reads=tf.data.AUTOTUNE
        ).map(
            self.read_data,
            num_parallel_calls=tf.data.AUTOTUNE
        ).batch(
            batch_size=1
        ).prefetch(tf.data.AUTOTUNE)

        records = [record for record in iter]
        return records

    def read_sample(self, instance):
        """
        Reads one sample from the dataset (one annotation file).

        Parameters
        ----------
            instance

        Returns
        -------
            gt_instance: dict
                This contains information regarding the ground truth:

                    .. code-block:: python

                        {
                            'image': np.ndarray image,
                            'height': The height of the image,
                            'width': The width of the image,
                            'boxes': The bounding boxes,
                            'labels': labels,
                            'image_path': The path to the image
                        }
        Raises
        ------
            None
        """
        img, boxes, labels, height, width, file_path = instance
        labels = labels.numpy()[0]
        if len(self.labels):
            labels = self.check_labels_type(labels)
        else:
            labels = labels.numpy()[0]

        return {
            'image': img.numpy()[0],
            'height': height.numpy()[0],
            'width': width.numpy()[0],
            'boxes': boxes.numpy()[0],
            'labels': labels,
            'image_path': file_path.numpy()[0].decode()
        }
