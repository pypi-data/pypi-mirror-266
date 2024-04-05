# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.writers.core import Writer
import numpy as np
from os import path

class TensorBoardWriter(Writer):
    """
    Used to publish the images and the metrics onto TensorBoard.
    
    Parameters
    ----------
        logdir: str
            This is the path to the tfevents file.

    Raises
    ------
        None
    """
    def __init__(
        self,
        logdir=None
        ):
        super(TensorBoardWriter, self).__init__()

        self.error_message = ("TensorFlow library is needed to " + 
                              "allow tensorboard functionalities")
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(self.error_message)

        self.logdir = logdir
        self.writer = None
        if logdir:
            self.writer = tf.summary.create_file_writer(self.logdir)

    def __call__(self, image, image_path, step=0):
        """
        When it is called, it publishes the images onto tensorboard.
        
        Parameters
        ----------
            image: (height, width, 3) np.ndarray
                The image array to display to tensorboard.

            image_path: str
                The path to the image.

            step: int
                This represents the number of the current epoch when training
                a model.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(self.error_message)

        with self.writer.as_default():
            nimage = np.expand_dims(image, 0)
            tf.summary.image(
                path.basename(image_path),
                nimage,
                step=step)
            self.writer.flush()

    def publish_metrics(
            self,
            message,
            parameters=None,
            step=0,
            validation_type='detection'
        ):
        """
        Publishes the metric summary onto tensorboard.
       
        Parameters
        ----------
            message: dict
                This contains the validation metrics.
                See README.md (Method Parameters Format) for more information.

            parameters: dict
                This contains information regarding the model and
                validation parameters.
                See README.md (Method Parameters Format) for more information.

            step: int
                This is the iteration number which represents the
                epoch number when training a model.

            validation_type: str
                This is the type of validation performed
                (detection or segmentation).

        Returns
        -------
            None

        Raises
        ------
            None
        """
        try:
            import os
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            import tensorflow as tf
        except ImportError:
            raise MissingLibraryException(self.error_message)

        with self.writer.as_default():

            if validation_type.lower() == 'detection':
                header, summary, timings = \
                    self.format_detection_summary(message, parameters)
            elif validation_type.lower() == 'segmentation':
                header, summary, timings = \
                    self.format_segmentation_summary(message)
            elif validation_type.lower() == 'pose':
                header, summary, timings = \
                    self.format_pose_summary(message)
            if timings is None:
                timings = "None"

            tf.summary.text(
                header,
                summary,
                step=step)
            tf.summary.text(
                "Timing Results",
                timings,
                step=step)
            self.writer.flush()

        return header, summary, timings

class TrainingTensorBoardWriter(TensorBoardWriter):
    """
    Used to publish metrics on training a model.
   
    Parameters
    ----------
        writer: TF.summary file writer object
            This is the writer object defined in trainer.

    Raises
    ------
        None
    """
    def __init__(
            self,
            writer
        ):
        super(TrainingTensorBoardWriter, self).__init__()
        self.writer = writer
