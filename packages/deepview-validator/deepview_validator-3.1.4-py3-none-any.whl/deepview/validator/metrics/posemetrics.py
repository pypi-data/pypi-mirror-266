# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.metrics.core import Metrics
import numpy as np

class PoseMetrics(Metrics):
    """
    Computes the mean squared error between angles for \
        detection and ground truth for pose.

    Parameters
    ----------
        posedatacollection: PoseDataCollection
            This is a container for the prediction and the ground truth
            angles.

    Raises
    ------
        None
    """
    def __init__(
            self,
            posedatacollection=None
            ):
        
        super(PoseMetrics, self).__init__()
        self.posedatacollection = posedatacollection

    def compute_overall_metrics(self):
        """
        Calculates the pose metrics with mean squared error for each angle. 

        Parameters
        ----------
            None

        Returns
        -------
            overall_metrics: np.ndarray
                This contains the mean squared error for each angle.

        Raises
        ------
            None
        """
        pose_label_data_list = self.posedatacollection.get_pose_data_list()
        overall_metrics = np.zeros(len(pose_label_data_list))
        for i, pose_data in enumerate(pose_label_data_list):
            overall_metrics[i] = self.mean_absolute_error(
                pose_data.get_y_true(), pose_data.get_y_pred())
        return overall_metrics