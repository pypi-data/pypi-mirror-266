# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import numpy as np

class SegmentationDataCollection:
    """
    Acts as a container of SegmentationLabelData objects \
        for each label and provides methods to capture the total \
            number of ground truths, true positives, false positives, \
                and false negatives for each pixel in the entire \
                    dataset that allows calculation of the overall metrics.
    
    Parameters
    ----------
        None

    Raises
    ------
        ValueError
            Raised if the provided parameters in certain methods 
            does not conform to the specified data type.
    """
    def __init__(self):
        # A list containing the RawDataLabel objects for each label.
        self.label_data_list = list()
        # Total number of ground truths in the dataset.
        self.total_gt = 0
        # Unique labels
        self.labels = list()

    @staticmethod
    def validate_num_parameter(num):
        """
        Validates input parameter num to be of type integer only.
        Used to check when adding the number of ground truths, \
            true positives, false positives, and false negatives \
                to be integers.
        
        Parameters
        ----------
            num: int
                The parameter to validate.

        Returns
        -------
            num: int
                The validated integer type parameter.

        Raises
        ------
            ValueError
                Raised if the input parameter is not of type integer.
        """
        if not (isinstance(num, (int, np.integer))):
            raise ValueError(
                "The provided num has an incorrect type: {}. ".format(
                    type(num)) + "Can only accept integer type.")
        else:
            return num

    def add_gt(self, num=1):
        """
        This method adds the number of recorded \
            ground truths of the dataset.
        
        Parameters
        ----------
            num: int
                The number of ground truths (pixels) to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num are not integers 
                or the value for num is a negative integer.
        """
        num = self.validate_num_parameter(num)
        if num < 0:
            raise ValueError(
                "num cannot be a negative integer, {}".format(num))
        else:
            self.total_gt += num

    def get_gt(self):
        """
        Grabs the number of recorded ground truths.
        
        Parameters
        ----------
            None

        Returns
        -------
            total ground truths: int
                The number of pixel ground truths.

        Raises
        ------
            None
        """
        return self.total_gt

    def add_label_data(self, label):
        """
        Adds a SegmentationLabelData object for the label.
        
        Parameters
        ----------
            label: str or int
                The string label or the integer index
                to place as a data container.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.label_data_list.append(SegmentationLabelData(label))

    def get_label_data(self, label):
        """
        Grabs the SegmentationLabelData object by label.
        
        Parameters
        ----------
            label: str or int
                A unique string label or integer index from the dataset.

        Returns
        -------
            None if the object does not exist.

            label_data: DetectionLabelData
                The data container of the label specified.

        Raises
        ------
            None
        """
        for label_data in self.label_data_list:
            if label_data.get_label() == label:
                return label_data
        return None

    def get_label_data_list(self):
        """
        Grabs the list containing the SegmentationLabelData objects.
        
        Parameters
        ----------
            None

        Returns
        -------
            label_data_list: list or np.ndarray
                The list containing the DetectionLabelData objects.

        Raises
        ------
            None
        """
        return self.label_data_list

    def get_labels(self):
        """
        Grabs the list containing the recorded \
            unique string or integer index labels.
        
        Parameters
        ----------
            None

        Returns
        -------
            labels: list or np.ndarray
                The list containing the unique string or integer
                index labels.

        Raises
        ------
            None
        """
        return self.labels

    def capture_class(self, class_labels, labels):
        """
        Records the unique labels encountered \
            in the prediction and ground truth and creates a \
                container (SegmentationLabelData) for the label \ 
                    found in the model predictions and ground truth.
        
        Parameters
        ----------
            class_labels: list of int.
                All unique indices for the classes found from the ground
                truth and the model predictions.

            labels: list or np.ndarray
                This list contains unique string labels for the classes found.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                This method will raise an exception
                if the parameter for class_labels
                does not contain integers.
        """
        for label_id in class_labels:
            if (isinstance(label_id, (int, np.integer))):
                if labels is not None:
                    label = labels[label_id]
                else:
                    label = label_id
                if label == " ":
                    continue
                else:
                    if label not in self.labels:
                        self.add_label_data(label)
                        self.labels.append(label)
            else:
                raise ValueError(
                    "The provided class_labels does not contain integers: {}"
                    .format(type(label_id)))

    def sum_outcomes(self):
        """
        Adds the total number of true positives, \
            false positives, and false negatives in the dataset.
        
        Parameters
        ----------
            None

        Returns
        -------
            outcomes: int
                The total number of true positives, false positives,
                and false negatives captured.

        Raises
        ------
            None
        """
        total_tp, total_fp, total_fn = 0, 0, 0
        for label_data in self.label_data_list:
            total_tp += label_data.tps
            # To avoid double counting
            if label_data.get_label() == "background":
                continue

            total_fp += label_data.fps
            total_fn += label_data.fns
            # Total number of ground truths in the dataset.
            self.total_gt = total_tp + total_fp + total_fn
        return total_tp, total_fn, total_fp

class SegmentationLabelData:
    """
    Acts a container that stores the total number of true positives, \
        false positives, false negatives per label that allows calculation of \
            mean average metrics.
    
    Parameters
    ----------
        label: str or int
            The unique string or integer index label to base the container.

    Raises
    ------
        ValueError
            Raised if the provided parameters do not conform 
            to the specified data type in the method.
    """
    def __init__(
        self,
        label
    ):
        self.label = label
        # Total number of ground truths of the label
        self.gt = 0
        # Total number of true positives, false positives, extra false
        # positives, false negatives of the class.
        self.tps, self.fps, self.fns = 0, 0, 0

    def get_label(self):
        """
        Grabs the class label being evaluated.
        
        Parameters
        ----------
            None

        Returns
        -------
            label: str or int
                The string or integer index label.

        Raises
        ------
            None
        """
        return self.label

    def set_label(self, new_label):
        """
        Sets the label to a different label.
        
        Parameters
        ----------
            new_label: str or int
                The label to change.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided label is 
                neither string nor integer.
        """
        if not (isinstance(new_label, (str, int))):
            raise ValueError(
                "The provided label has an incorrect type: {}. ".format(
                type(new_label)) + "Can only accept string or integer type.")
        else:
            self.label = new_label

    def add_gt(self, num=1):
        """
        Adds the number of ground truth pixels for \
            the class label from the entire dataset.
        
        Parameters
        ----------
            num: int
                The number of ground truth pixels to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num is not of type int.
        """
        num = SegmentationDataCollection.validate_num_parameter(num)
        self.gt += num

    def get_gt(self):
        """
        Grabs the number of ground truths \
            that is currently recorded.
        
        Parameters
        ----------
            None

        Returns
        -------
            self.gt: int
                The number of ground truths.

        Raises
        ------
            None
        """
        return self.gt

    def get_tp(self):
        """
        Grabs the total number of recorded \
            true positives.
        
        Parameters
        ----------
            None

        Returns
        -------
            tp: int
                The number of recorded true positives.

        Raises
        ------
            None
        """
        return self.tps

    def get_fn(self):
        """
        Grabs the total number of recorded \
            false negatives.
        
        Parameters
        ----------
            None

        Returns
        -------
            fp: int
                The number of recorded false negatives.

        Raises
        ------
            None
        """
        return self.fns

    def get_fp(self):
        """
        Grabs the total number of recorded \
            false positives.
        
        Parameters
        ----------
            None

        Returns
        -------
            fp: int
                The number of recorded false positives.

        Raises
        ------
            None
        """
        return self.fps

    def add_tp(self, num=1):
        """
        Adds the number of true positives gathered.
        A true positive is when the prediction pixel is a \
            1 and the ground truth pixel is a 1. 
        A true positive is also when the prediction pixel \
            is a 0 and the ground truth pixel is a 0.
        
        Parameters
        ----------
            num: int
                The number of true positives to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num is not of type int.
        """
        num = SegmentationDataCollection.validate_num_parameter(num)
        self.tps += num

    def add_fn(self, num=1):
        """
        Adds the number of false negatives gathered.
        A false negative is when the prediction pixel is a \
            0 but the ground truth pixel is a 1.
        
        Parameters
        ----------
            num: int
                The number of false negatives to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num is not of type int.
        """
        num = SegmentationDataCollection.validate_num_parameter(num)
        self.fns += num

    def add_fp(self, num=1):
        """
        Adds the number of false positives gathered.
        A false positive is when the prediction pixel is a \
            1 but the ground truth pixel is a 0.

        Parameters
        ----------
            num: int
                The number of false positives to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num is not of type int.
        """
        num = SegmentationDataCollection.validate_num_parameter(num)
        self.fps += num