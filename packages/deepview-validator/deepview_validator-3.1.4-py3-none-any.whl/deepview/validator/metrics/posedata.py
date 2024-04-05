# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import numpy as np

class PoseDataCollection:
    """
    This is a container of PoseLabelData objects each contains \
        angles for either roll, pitch, yaw.

    Parameters
    ----------
        None

    Raises
    ------
        None
    """
    def __init__(self) -> None:
        
        self.pose_data_list = list()
        self.angle_names = list()

    def add_pose_data(self, label):
        """
        Adds PoseLabelData object per label.
        
        Parameters
        ----------
            label: str
                The string label to place as a data container. 
                Can be either 'roll', 'pitch', or 'yaw'.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        if not (isinstance(label, str)):
            raise ValueError(
                "Unexpected input type is provided for label {}. ".format(
                    type(label)) + "It can only be of type string.")
        else:
            self.pose_data_list.append(PoseLabelData(label))

    def get_pose_data(self, label):
        """
        Grabs the PoseLabelData object by label.
        
        Parameters
        ----------
            label: str
                The name of the angle.

        Returns
        -------
            None if the object does not exist.

            pose_data: PoseLabelData
                The data container of the angle name specified.

        Raises
        ------
            None
        """
        for pose_data in self.pose_data_list:
            if pose_data.get_label() == label:
                return pose_data
        return None

    def get_pose_data_list(self):
        """
        Grabs the list containing the PoseLabelData objects.
        
        Parameters
        ----------
            None

        Returns
        -------
            pose_data_list: list 
                The list containing the PoseLabelData objects.

        Raises
        ------
            None
        """
        return self.pose_data_list
    
    def reset_containers(self):
        """
        Resets the pose_data_list container to an empty list.
        
        Parameters
        ----------
            None

        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.pose_data_list = []

    def capture_angle_names(self, name):
        """
        Creates a PoseLabelData object based on the \
            provided angle name if it does not exist yet.
        
        Parameters
        ----------
            name: str
                The name of the angle.

        Returns
        -------
            None
        
        Raises
        ------
            None
        """
        if name not in self.angle_names:
            self.add_pose_data(name)
            self.angle_names.append(name)

    def store_angle(self, name, dt_angle, gt_angle):
        """
        Stores the angle in the object with the specified name.

        Parameters
        ----------
            name: str
                The name of the angle.

            dt_angle: float
                The detection angle.
            
            gt_angle: float
                The ground truth angle.

        Returns
        -------
            None

        Raises
        ------
            None            
        """
        posedata = self.get_pose_data(name)
        if posedata is None:
            raise ValueError(
                f"No PoseData container is associated with this angle: {name}")
        posedata.add_y_pred(dt_angle)
        posedata.add_y_true(gt_angle)

    def store_angles(self, dt_angles, gt_angles):
        """
        Evaluates the lengths of the provided angles. 
        If it is three it assumes the angles are roll, pitch, and yaw. 
        If it is four, it assumes the angles are quaternion. 
        Also provides flexibility for other angle lengths, \
            but names them as angle_1, angle_2, etc..

        Parameters
        ----------
            dt_angles: list or np.ndarray
                An array that contains the detection angles.

            gt_angles: list or np.ndarray
                An array that contains the ground truth angles.

        Returns
        -------
            None

        Raises
        ------
            None            
        """
        if len(gt_angles) != len(dt_angles):
            raise ValueError("The lengths of the provided angles for " + 
                             "detection and ground truth are not the same.")

        if len(gt_angles) == 3:
            # Euler Angles
            for name, dt_angle, gt_angle in zip(
                ["roll", "pitch", "yaw"], dt_angles, gt_angles):
                self.capture_angle_names(name)
                self.store_angle(name, dt_angle, gt_angle)

        elif len(gt_angles) == 0:
            for name in ["roll", "pitch", "yaw"]:
                self.capture_angle_names(name)
                self.store_angle(name, np.nan, np.nan)

        elif len(gt_angles) == 4:
            # Quaternion Angles
            for name, dt_angle, gt_angle in zip(
                ["real", "i", "j", "k"], dt_angles, gt_angles):
                self.capture_angle_names(name)
                self.store_angle(name, dt_angle, gt_angle)
        else:
            for i, (dt_angle, gt_angle) in enumerate(
                zip(dt_angles, gt_angles)):
                self.capture_angle_names("angle_{}".format(i))
                self.store_angle("angle_{}".format(i), dt_angle, gt_angle)

class PoseLabelData:
    """
    This is a container of angles for one \
        specific angle for both prediction and ground truth.

    Parameters
    ----------
        label: str
            This is the angle name (Ex. roll, pitch, or yaw).

    Raises
    ------
        None
    """
    def __init__(self, label):
        self.label = label

        # The true angles
        self.y_true = list()
        # The predicted angles
        self.y_pred = list()

    def get_label(self):
        """
        Returns the name of the angle representing this container.

        Parameters
        ----------
            None

        Returns
        -------
            label: str
                The name of the angle.

        Raises
        ------
            None
        """
        return self.label
    
    def set_label(self, label):
        """
        Sets the name of the angle representing this container.

        Parameters
        ----------
            label: str
                The name of the angle to set for this container.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.label = label
    
    def add_y_true(self, gt_angle):
        """
        Adds a ground truth angle to the ground truth list.

        Parameters
        ----------
            gt_angle: float
                The ground truth angle.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.y_true.append(gt_angle)

    def add_y_pred(self, dt_angle):
        """
        Adds a predicted angle to the predicted list.

        Parameters
        ----------
            dt_angle: float
                The model prediction angle.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.y_pred.append(dt_angle)

    def get_y_true(self):
        """
        Returns the list of ground truth angles.

        Parameters
        ----------
            None

        Returns
        ------- 
            y_true: list
                A list of ground truth angles.

        Raises
        ------
            None
        """
        return self.y_true
    
    def get_y_pred(self):
        """
        Returns the list of predicted angles.

        Parameters
        ----------
            None

        Returns
        ------- 
            y_pred: list
                A list of predicted angles.

        Raises
        ------
            None
        """
        return self.y_pred