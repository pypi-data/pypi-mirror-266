# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import numpy as np

class DetectionDataCollection:
    """
    Acts as a container for DetectionLabelData objects \
        for each label and provides methods to capture the \
            total number of true positives, false positives, \
                and false negatives in the dataset.
    
    Parameters
    ----------
        None

    Raises
    ------
        ValueError
            Raised if the provided parameters in certain methods 
            does not conform to the specified data type or the 
            parameters are out of bounds. i.e. The thresholds 
            provided are greater than 1 or less than 0.
    """
    def __init__(self):
        # A list containing the DetectionLabelData objects for each label.
        self.label_data_list = list()
        # Total number of ground truths in the dataset.
        self.total_gt = 0
        # A list containing the strings of unique labels.
        self.labels = list()
        # container for all ground truth and detections.
        self.instances = dict()
        # A container to store all matches summary.
        self.summary = dict()

    def initialize_confusion_data(
            self, 
            dataset_labels,
            iou_threshold,
            score_threshold
        ):
        """
        Creates the confusion data array given all the \
            possible unique labels in the dataset \
                including background to determine the size of the array.

        Parameters
        ----------
            dataset_labels: list or np.ndarray
                This contains all the unique string labels in
                the dataset.

            iou_threshold: float
                The validation IoU set in the command line.

            score_threshold: float
                The validation score set in the command line.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.dataset_labels = dataset_labels
        # confusion matrix data
        self.confusion_data = np.zeros(
            (len(self.dataset_labels), len(self.dataset_labels)))
        self.iou_t = iou_threshold
        self.score_t = score_threshold
        
    def get_confusion_data(self):
        """
        Returns the data used to create the confusion matrix.

        Parameters
        ----------
            None

        Returns
        -------
            confusion_data: np.ndarray
                A sqaure matrix where the rows are the 
                prediction classes and the columns are the 
                ground truth classes.

            dataset_labels: list
                This contains the unique string labels in the
                dataset.

        Raises
        ------
            None
        """
        return self.confusion_data, self.dataset_labels
        
    def append_instance(self, key, instance):
        """
        Appends an instance inside the instances container.

        Parameters
        ----------
            key: str
                The name to point to the instance.

            instance: dict

                .. code-block:: python

                    {
                        'gt_instance': {
                            'height': height,
                            'width': width,
                            'boxes': list bounding boxes,
                            'labels': list of labels
                        },
                        'dt_instance': {
                            'boxes': list of prediction bounding boxes,
                            'labels': list of prediction labels,
                            'scores': list of confidence scores
                        }
                    }
        
        Returns
        -------
            None

        Raises
        ------
            None
        """
        self.instances[key] = instance

    def get_instances(self):
        """
        Returns the instances for all captured detections \
            and all captured ground truth.

        Parameters
        ----------
            None

        Returns
        -------
            instances: dict
                The container for all captured detections and ground truth.

        Raises
        ------
            None
        """
        return self.instances

    @staticmethod
    def validate_score(score, min=0., max=1.):
        """
        Validates the confidence score or the score threshold \
            to be a floating type and does not exceed defined \
                bounds (0...1).

        Parameters
        ----------
            score: float
                The score to validate.

            min: float
                The minimum acceptable score.

            max: float
                The maximum acceptable score.

        Returns
        -------
            score: float
                The validated score.

        Raises
        ------
            ValueError
                Raised if the provided score is not floating point
                type or it is out bounds (less than 0 or greater than 1).
        """
        if not isinstance(score, (float, np.floating)):
            raise ValueError(
                "The provided score is not of numeric type: float. " +
                "Provided with type: {}".format(type(score)))
        
        if score < min:
            return min
        elif score > max:
            return max
        else:
            return score

    @staticmethod
    def validate_iou(iou, min=0., max=1.):
        """
        Validates the IoU score or the IoU threshold \
            to be a floating type and does not exceed \
                defined bounds (0...1).

        Parameters
        ----------
            iou: float
                The iou to validate.

            min: float
                The minimum acceptable iou.

            max: float
                The maximum acceptable iou.

        Returns
        -------
            iou: float
                The validated IoU.

        Raises
        ------
            ValueError
                Raised if the provided IoU is not floating point type
                or it is out bounds (less than 0 or greater than 1).
        """
        if not isinstance(iou, (float, np.floating)):
            raise ValueError(
                "The provided iou is not of numeric type: float. " +
                "Provided with iou: {}".format(type(iou))) 
        
        if iou < min:
            return min
        elif iou > max:
            return max
        else:
            return iou

    def add_gt(self, num=1):
        """
        Adds the number of recorded ground truths in the dataset.

        Parameters
        ----------
            num: int
                The number of ground truths to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num are not 
                integers or the value for num is a negative integer.
        """
        if not isinstance(num, (int, np.integer)):
            raise ValueError(
                "Unexpected input type is provided for num {}. ".format(
                    type(num)) + "It can only be of type integer.")
        else:
            if num < 0:
                raise ValueError(
                    "num cannot be a negative integer, {}".format(num))
            else:
                self.total_gt += num

    def get_gt(self):
        """
        Gets the number of recorded ground truths.
        
        Parameters
        ----------
            None

        Returns
        -------
            total ground truths: int
                The number of ground truths.

        Raises
        ------
            None
        """
        return self.total_gt

    def add_label_data(self, label):
        """
        Adds DetectionLabelData object per label.
        
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
        if not (isinstance(label, (str, int, np.integer))):
            raise ValueError(
                "Unexpected input type is provided for label {}. ".format(
                    type(label)) + "It can only be of type integer or string.")
        else:
            self.label_data_list.append(DetectionLabelData(label))

    def get_label_data(self, label):
        """
        Grabs the DetectionLabelData object by label.

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
        Gets the list containing the DetectionLabelData objects.

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
        Gets the list containing the recorded \
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
    
    def reset_containers(self):
        """
        Resets the label_data_list container to an empty list \
            and resets the labels captured to an empty list \
                and the number of ground truths to 0.

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
        self.label_data_list = []
        self.labels = []
        self.total_gt = 0

    def capture_class(self, labels):
        """
        Records the unique labels encountered \
            in the prediction and ground truth and creates a \
                container (DetectionLabelData) for eac unique label found.

        Parameters
        ----------
            labels: list() or np.ndarray
                This list contains labels for one image.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        for label in labels:
            if isinstance(label, str):
                if label.lower() in ["background", " ", ""]:
                    continue
            if label not in self.labels:
                self.add_label_data(label)
                self.labels.append(label)

    def categorize_simple(
            self,
            index_matches,
            index_extra_dt,
            index_missed_gt,
            iou_list,
            gt_labels,
            dt_labels,
            scores
    ):
        # Matched Predictions
        for match in index_matches:
            dt_label, gt_label = dt_labels[match[0]], gt_labels[match[1]]
            iou, score = iou_list[match[0]], scores[match[0]]

            if dt_label != gt_label:
                label_data = self.get_label_data(dt_label)
                if label_data is not None:
                    label_data.add_class_fp(iou, score)

            label_data = self.get_label_data(gt_label)
            if label_data is not None:
                label_data.add_gt()
                if dt_label == gt_label:
                    label_data.add_tp(iou, score)

            # Fill confusion matrix
            try:
                if score >= self.score_t:
                    if isinstance(dt_label, (int, np.integer)):
                        dt_label = self.dataset_labels[dt_label]
                    if isinstance(gt_label, (int, np.integer)):
                        gt_label = self.dataset_labels[gt_label]

                    dt_index = self.dataset_labels.index(dt_label)
                    gt_index = self.dataset_labels.index(gt_label)
                    if iou >= self.iou_t:
                        self.confusion_data[dt_index][gt_index] += 1
                    else:
                        self.confusion_data[dt_index][0] += 1
                        self.confusion_data[0][gt_index] += 1
            except AttributeError:
                pass

        # Extra Predictions.
        for extra in index_extra_dt: 
            dt_label, score = dt_labels[extra], scores[extra]
            label_data = self.get_label_data(dt_label)
            if label_data is not None:
                label_data.add_local_fp(score)

            try:
                if score >= self.score_t:
                    if isinstance(dt_label, (int, np.integer)):
                        dt_label = self.dataset_labels[dt_label]
                    self.confusion_data[
                        self.dataset_labels.index(dt_label)][0] += 1
            except AttributeError:
                pass

        # Missed Predictions.
        for missed in index_missed_gt:
            gt_label = gt_labels[missed]
            label_data = self.get_label_data(gt_label)
            if label_data is not None:
                label_data.add_gt()
            try:
                if isinstance(gt_label, (int, np.integer)):
                        gt_label = self.dataset_labels[gt_label]
                self.confusion_data[0][
                    self.dataset_labels.index(gt_label)] += 1
            except AttributeError:
                pass
        self.add_gt(len(gt_labels))

    def categorize(
            self,
            image,
            index_matches,
            index_extra_dt,
            index_missed_gt,
            iou_list,
            gt_labels,
            dt_labels,
            gt_boxes,
            dt_boxes,
            scores
        ):
        """
        Defines the predictions as either true positives, false positives, \
            or false negatives.

        Parameters
        ----------
            index_matches: list or np.ndarray
                This contains the indices of each match
                [[index_dt, index_gt]...].

            index_extra_dt: list or np.ndarray
                This contains indices of model
                predictions captured as local fp.

            index_missed_gt: list or np.ndarray
                This contains indices of ground truth that were not matched.

            iou_list: list or np.ndarray
                This contains the IoU values of all
                matches in respective order.

            gt_labels: list or np.ndarray
                This contains the ground truth string or integer index labels.

            dt_labels: list or np.ndarray
                This contains the model prediction string
                or integer index labels.

            scores: list or np.ndarray
                This contains the score values for each model prediction.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided iou or score does not conform 
                to the specified data type or the parameters are 
                out of bounds. i.e. The provided iou or score is 
                greater than 1 or less than 0.
        """
        current_summary = list()
        # Matched Predictions
        for match in index_matches:
            dt_label, gt_label = dt_labels[match[0]], gt_labels[match[1]]
            iou, score = iou_list[match[0]], scores[match[0]]

            # Fill summary
            gt_box, dt_box = list(gt_boxes[match[1]]), list(dt_boxes[match[0]])
            gt_box.insert(4, gt_label)
            dt_box.insert(4, dt_label)

            if score >= self.score_t:
                current_summary.append(
                    [
                        tuple([x if isinstance(x, str) else float(x) for x in gt_box]), 
                        tuple([x if isinstance(x, str) else float(x) for x in  dt_box]), 
                        (float(iou),)
                    ] # If it is a classification FP or TP.
                )
            else:
                current_summary.append(
                [
                    tuple([x if isinstance(x, str) else float(x) for x in  gt_box]), 
                    None, 
                    None
                ] # If it is a False Negative.
            )

            if dt_label != gt_label:
                label_data = self.get_label_data(dt_label)
                if label_data is not None:
                    label_data.add_class_fp(iou, score)

            label_data = self.get_label_data(gt_label)
            if label_data is not None:
                label_data.add_gt()
                if dt_label == gt_label:
                    label_data.add_tp(iou, score)

            # Fill confusion matrix
            try:
                if score >= self.score_t:
                    if isinstance(dt_label, (int, np.integer)):
                        dt_label = self.dataset_labels[dt_label]
                    if isinstance(gt_label, (int, np.integer)):
                        gt_label = self.dataset_labels[gt_label]

                    dt_index = self.dataset_labels.index(dt_label)
                    gt_index = self.dataset_labels.index(gt_label)
                    if iou >= self.iou_t:
                        self.confusion_data[dt_index][gt_index] += 1
                    else:
                        self.confusion_data[dt_index][0] += 1
                        self.confusion_data[0][gt_index] += 1
            except AttributeError:
                pass

        # Extra Predictions.
        for extra in index_extra_dt: 
            dt_label, score = dt_labels[extra], scores[extra]

            # Fill summary
            if score >= self.score_t:
                dt_box = list(dt_boxes[extra])
                dt_box.insert(4, dt_label)
                current_summary.append(
                    [
                        None, 
                        tuple([x if isinstance(x, str) else float(x) for x in dt_box]), 
                        None
                    ] # If it is a localization FP.
                )

            label_data = self.get_label_data(dt_label)
            if label_data is not None:
                label_data.add_local_fp(score)

            try:
                if score >= self.score_t:
                    if isinstance(dt_label, (int, np.integer)):
                        dt_label = self.dataset_labels[dt_label]
                    self.confusion_data[
                        self.dataset_labels.index(dt_label)][0] += 1
            except AttributeError:
                pass

        # Missed Predictions.
        for missed in index_missed_gt:
            gt_label = gt_labels[missed]

            # Fill summary
            gt_box = list(gt_boxes[missed])
            gt_box.insert(4, gt_label)
            current_summary.append(
                [
                    tuple([x if isinstance(x, str) else float(x) for x in  gt_box]), 
                    None, 
                    None
                ] # If it is a False Negative.
            )

            label_data = self.get_label_data(gt_label)
            if label_data is not None:
                label_data.add_gt()
            try:
                if isinstance(gt_label, (int, np.integer)):
                        gt_label = self.dataset_labels[gt_label]
                self.confusion_data[0][
                    self.dataset_labels.index(gt_label)] += 1
            except AttributeError:
                pass
        self.add_gt(len(gt_labels))
        self.summary[image] = current_summary
       
    def sum_outcomes(self, iou_threshold, score_threshold):
        """
        Adds the total number of true positives, false negatives, \
            and false positives(localization and classification) \
                in the dataset at the specified validation IoU \
                    and score thresholds.

        Parameters
        ----------
            iou_threshold: float
                Validation IoU threshold to consider true positives.

            score_threshold: float
                Validation score threshold to filter predictions.

        Returns
        -------
            outcomes: list
                The total number of true positives,
                false positives (local and class), and false negatives.

        Raises
        ------
            ValueError
                Raised if the provided thresholds are not floating 
                types or they are out bounds (less than 0 or greater than 1).
        """
        score_threshold = self.validate_score(score_threshold)
        iou_threshold = self.validate_iou(iou_threshold)
        total_tp, total_class_fp, total_local_fp = 0, 0, 0
        for label_data in self.label_data_list:

            total_tp += label_data.get_tp_count(iou_threshold, score_threshold)
            total_class_fp += label_data.get_class_fp_count(
                iou_threshold, score_threshold)
            total_local_fp += label_data.get_local_fp_count(
                iou_threshold, score_threshold)

        total_fn = self.total_gt - (total_tp + total_class_fp)
        return [total_tp, total_fn, total_class_fp, total_local_fp]

class DetectionLabelData:
    """
    Acts a container that stores the total number of true positives, \
        false positives, false negatives per label and provides \
            methods to calculate the mean average metrics.

    Parameters
    ----------
        label: str or int
            The unique string or integer index label to base the container.

    Raises
    ------
        ValueError
            Raised if the provided parameters do not conform to 
            the specified data type in the method or the parameters 
            are out of bounds such as the IoU and score threshold 
            being greater than 1 or less than 0.
    """
    def __init__(
        self,
        label
    ):
        if not isinstance(label, (str, int, np.integer)):
            raise ValueError("The provided label is neither string nor int. " +
                             "Recieved type: {}".format(type(label)))
        
        self.label = label
        # Total number of ground truths of the label
        self.gt = 0
        # Contains (IoU, score) values for predictions marked as true positives
        self.tps = list()
        # Contains (IoU, score) values for predictions marked as classification
        # false positives
        self.class_fps = list()
        # Contains score values for predictions captured as localization false
        # positives
        self.local_fps = list()
        
        # The number of true positives that became localization false positives
        # due to the IoU less than the set threshold
        self.tp2fp = 0

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
                Raised if the provided label is neither string nor integer.
        """
        if not (isinstance(new_label, (str, int, np.integer))):
            raise ValueError(
                "The provided label has an incorrect type: {}. ".format(
                type(new_label)) + "Can only accept string or integer type.")
        else:
            self.label = new_label

    def add_gt(self, num=1):
        """
        Adds the number of ground truth for the \
            class label from the entire dataset.

        Parameters
        ----------
            num: int
                The number of ground truths to add.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided num is not of type 
                int or num is a negative integer.
        """
        if not (isinstance(num, (int, np.integer))):
            raise ValueError(
                "The provided num has an incorrect type: {}. ".format(
                    type(num)) + "Can only accept integer type.")
        else:
            if num < 0:
                raise ValueError("The number of ground truths to add can " + 
                                 "can only be positive integers. " +
                                 "Recieved: {}".format(num))
            self.gt += num

    def get_gt(self):
        """
        Grabs the number of ground truths that \
            is currently recorded.

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

    def get_tp_scores(self):
        """
        Grabs the prediction scores marked \
            as true positives.

        Parameters
        ----------
            None

        Returns
        -------
            scores: np.ndarray
                The true positive scores.

        Raises
        ------
            None
        """
        if len(self.tps):
            return np.array(self.tps)[:, 1]
        else:
            return np.array([])

    def get_tp_iou(self):
        """
        Grabs the prediction IoUs marked \
            as true positives.

        Parameters
        ----------
            None

        Returns
        -------
            IoUs: np.ndarray
                The true positive IoU values.

        Raises
        ------
            None
        """
        if len(self.tps):
            return np.array(self.tps)[:, 0]
        else:
            return np.array([])

    def get_class_fp_scores(self):
        """
        Grabs the prediction scores marked as \
            classification false positives.

        Parameters
        ----------
            None

        Returns
        -------
            scores: np.ndarray
                The classification false positive scores.

        Raises
        ------
            None
        """
        if len(self.class_fps):
            return np.array(self.class_fps)[:, 1]
        else:
            return np.array([])

    def get_class_fp_iou(self):
        """
        Grabs the prediction IoUs marked as \
            classification false positives.

        Parameters
        ----------
            None

        Returns
        -------
            IoUs: np.ndarray
                The classification false positive IoUs.

        Raises
        ------
            None
        """
        if len(self.class_fps):
            return np.array(self.class_fps)[:, 0]
        else:
            return np.array([])

    def get_local_fp_scores(self):
        """
        Grabs the prediction scores marked as \
            localization false positives.

        Parameters
        ----------
            None

        Returns
        -------
            scores: np.ndarray
                The localization false positive scores.

        Raises
        ------
            None
        """
        if len(self.local_fps):
            return np.array(self.local_fps)
        else:
            return np.array([])
        
    def get_tp2fp(self):
        """
        Grabs the number of true positives \
            treated as localization false positives \
                due to the IoU being less than the set threshold.

        Parameters
        ----------
            None

        Returns
        -------
            count: int
                The number of these occurences.

        Raises
        ------
            None
        """
        return self.tp2fp

    def add_tp(self, iou, score):
        """
        Adds the true positive prediction IoU and \
            confidence score. A true positive is when the prediction \
                and the ground truth label matches and the IoU is \
                    greater than the set IoU threshold.
    
        Parameters
        ----------
            iou: float
                The IoU of the true positive prediction.

            score: float
                The confidence score of the true positive prediction.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided iou and score are not 
                floating types or they are out of bounds
                such as greater than 1 and less than 0.
        """
        score = DetectionDataCollection.validate_score(score)
        iou = DetectionDataCollection.validate_iou(iou)
        self.tps.append((iou, score))

    def add_class_fp(self, iou, score):
        """
        Adds the false positive (classification) prediction \
            IoU and confidence score. A false positive (classification) \
                is when the prediction and the ground truth labels don't \
                    match and the IoU is greater than the set IoU threshold.
    
        Parameters
        ----------
            iou: float
                The IoU of the classification false positive prediction.

            score: float
                The confidence score of the classification false
                positive prediction.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided iou and score 
                are not floating types or they are out of bounds
                such as greater than 1 and less than 0.
        """
        score = DetectionDataCollection.validate_score(score)
        iou = DetectionDataCollection.validate_iou(iou)
        self.class_fps.append((iou, score))

    def add_local_fp(self, score):
        """
        Adds the number of false positive (localization) captured.
        A false positive (localization) is when there is a \
            prediction but no ground truth.
        
        Parameters
        ----------
            score: float
                The confidence score of the localization
                false positive prediction.

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided score is not a floating 
                point type and is out bounds meaning it is
                greater than 1 or less than 0.
        """
        score = DetectionDataCollection.validate_score(score)
        self.local_fps.append(score)

    def add_tp2fp(self, iou_threshold, score_threshold):
        """
        Adds the number of potential true positives that became \
            localization false positives due to their IoU being less \
                than the defined IoU threshold. 
        
        Parameters
        ----------
            iou_threshold: float
                The IoU threshold set.

            score_threshold: float
                The score threshold set. 

        Returns
        -------
            None

        Raises
        ------
            ValueError
                Raised if the provided iou_threshold 
                and score_threshold are not floating types or 
                they are out of bounds such as greater than 1 and less than 0.
        """
        if len(self.tps):
            fp_iou = np.array(self.tps)[:, 0] < iou_threshold
            tp_score = np.array(self.tps)[:, 1] >= score_threshold
            # These are the IoUs for those TP that are less than threshold.
            #loc_iou = np.array(self.tps)[:, 0] * tp_score.astype(int)
            self.tp2fp += np.count_nonzero(fp_iou * tp_score)

    def get_tp_count(self, iou_threshold, score_threshold):
        """
        Grabs the number of true positives at the \
            specified IoU threshold and score threshold.
        
        Parameters
        ----------
            iou_threshold: float
                The IoU threshold to consider the true positives.

            score_threshold: float
                The score threshold to consider the predictions.

        Returns
        -------
            count: int
                The number of true positives at the specified
                IoU and score threshold.

        Raises
        ------
            ValueError
                Raised if the provided iou_threshold and 
                score_threshold are not floating types or 
                they are out of bounds such as greater than 1 and less than 0.
        """
        score_threshold = DetectionDataCollection.validate_score(
            score_threshold)
        iou_threshold = DetectionDataCollection.validate_iou(iou_threshold)
        if len(self.tps):
            tp_iou = np.array(self.tps)[:, 0] >= iou_threshold
            tp_score = np.array(self.tps)[:, 1] >= score_threshold
            return np.count_nonzero(tp_iou * tp_score)
        else:
            return 0

    def get_class_fp_count(self, iou_threshold, score_threshold):
        """
        Grabs the number of classification false positives at \
            the specified IoU and score threshold.

        Parameters
        ----------
            iou_threshold: float
                The IoU threshold to consider classification false positives.

            score_threshold: float
                The score threshold to consider predictions.

        Returns
        -------
            count: int
                The number of classification false positives at the
                specified IoU and score threshold.

        Raises
        ------
            ValueError
                Raised if the provided iou_threshold and 
                score_threshold are not floating types or 
                they are out of bounds such as greater than 1 and less than 0.
        """
        score_threshold = DetectionDataCollection.validate_score(
            score_threshold)
        iou_threshold = DetectionDataCollection.validate_iou(iou_threshold)
        if len(self.class_fps):
            fp_iou = np.array(self.class_fps)[:, 0] >= iou_threshold
            fp_score = np.array(self.class_fps)[:, 1] >= score_threshold
            return np.count_nonzero(fp_iou * fp_score)
        else:
            return 0

    def get_local_fp_count(self, iou_threshold, score_threshold):
        """
        Grabs the number of localization false positives \
            at the specified IoU and score threshold.
            The IoU threshold is needed because true positives that have \
                an IoU less than the set IoU threshold will be considered as \
                    localization false positives.
        
        Parameters
        ----------
            iou_threshold: float
                The IoU threshold to consider true positives as local
                false positives.

            score_threshold: float
                The score threshold to consider predictions.

        Returns
        -------
            count: int
                The number of localization false positives at the
                specified IoU and score threshold.

        Raises
        ------
            ValueError
                Raised if the provided iou_threshold and 
                score_threshold are not floating types or 
                they are out of bounds such as greater than 1 and less than 0.
        """
        score_threshold = DetectionDataCollection.validate_score(
            score_threshold)
        iou_threshold = DetectionDataCollection.validate_iou(iou_threshold)
        local_fp = 0

        if len(self.tps):
            # Any predictions that are below the IoU thresholds are
            # localization false positives.
            fp_iou = np.array(self.tps)[:, 0] < iou_threshold
            tp_score = np.array(self.tps)[:, 1] >= score_threshold
            local_fp += np.count_nonzero(fp_iou * tp_score)

        if len(self.class_fps):
            class_fp_iou = np.array(self.class_fps)[:, 0] < iou_threshold
            class_fp_score = np.array(self.class_fps)[:, 1] >= score_threshold
            local_fp += np.count_nonzero(class_fp_iou * class_fp_score)

        local_fp += np.count_nonzero(
            np.array(self.local_fps) >= score_threshold)
        return local_fp

    def get_fn_count(self, iou_threshold, score_threshold):
        """
        Grabs the number of false negatives at the specified \
            IoU threshold and score threshold. Score threshold is \
                needed because by principle fp = gt - tp, and score \
                    and IoU threshold is required to find the number \
                        of true positives.
        
        Parameters
        ----------
            iou_threshold: float
                The IoU threshold to consider true positives.

            score_threshold: float
                The score threshold to consider predictions.

        Returns
        -------
            count: int
                The number of false negatives at the specified
                IoU and score threshold.

        Raises
        ------
            ValueError
                Raised if the provided iou_threshold and \
                    score_threshold are not floating types or \
                        they are out of bounds such as greater \
                            than 1 and less than 0.
        """
        return self.gt - self.get_tp_count(iou_threshold, score_threshold)