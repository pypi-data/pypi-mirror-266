# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.metrics.detectionutils import match_gt_dt, filter_dt, \
    nan_to_last_num, clamp_boxes, ignore_boxes
from deepview.validator.exceptions import ZeroUniqueLabelsException
from deepview.validator.metrics.core import Metrics
import numpy as np

class DetectionMetrics(Metrics):
    """
    Provides methods to calculate::

        1. precision.
                -> overall precision.

                -> mAP 0.5, 0.75, 0.5-0.95.
        2. recall.
                -> overall recall.

                -> mAR 0.5, 0.75, 0.5-0.95.
        3. accuracy.
                -> overall accuracy.

                -> mACC 0.5, 0.75, 0.5-0.95.

    Other calculations such as IoU, false positive ratios, \
        precision vs recall data are also handled in this class.
    
    Parameters
    ----------
        detectiondatacollection: DetectionDataCollection
            This contains the number of ground truths in
            the dataset and tp, fp, and fn per class.

    Raises
    ------
        InvalidIoUException
            Raised if the calculated IoU is invalid. 
            i.e. less than 0 or greater than 1.

        DivisionByZeroException
                Raised if a division of zero is encountered 
                when calculating precision, recall, or accuracy.

        ZeroUniqueLabelsException
                Raised if the number of unique labels captured is zero.

        ValueError
            Raised if the provided parameters in certain methods 
            does not conform to the specified data type or the 
            parameters are out of bounds. i.e. The thresholds provided
            are greater than 1 or less than 0.
    """
    def __init__(
        self,
        detectiondatacollection=None,
        clamp=None,
        ignore=None,
        metric="iou"
    ):
        super(DetectionMetrics, self).__init__()
        self.detectiondatacollection = detectiondatacollection
        self.clamp_box = clamp
        self.ignore_box = ignore
        self.metric = metric
    
    def get_overall_metrics(
        self,
        total_tp,
        total_fn,
        total_class_fp,
        total_local_fp
        ):
        """
        Returns the overall precision, recall, and accuracy.

            1. overall precision = sum tp / \
                (sum tp + sum fp (localization + classification)).
            2. overall recall = sum tp / \
                (sum tp + sum fn + sum fp (localization)).
            3. overall accuracy  = sum tp / \
                (sum tp + sum fn + sum fp (localization + classification)).

        Parameters
        ----------
            total_tp: int
                Total number of true positives in the dataset.

            total_fn: int
                Total number of false negatives in the dataset.

            total_class_fp: int
                Total number of classification false positives in the dataset.

            total_local_fp: int
                Total number of localization false positives in the dataset.

        Returns
        -------
            overall metrics: np.ndarray (1, 3)
                This contains overall precision, overall recall,
                and overall accuracy.

        Raises
        ------
            DivisionByZeroException
                Raised if a division of zero is encountered 
                when calculating precision, recall, or accuracy.
        """
        overall_metrics = np.zeros(3)
        if total_tp == 0:
            if total_class_fp + total_local_fp == 0:
                overall_metrics[0] = np.nan
            if total_fn == 0:
                overall_metrics[1] = np.nan
            if total_class_fp + total_local_fp + total_fn == 0:
                overall_metrics[2] = np.nan
        else:
            overall_metrics[0] = self.compute_precision(
                total_tp, total_class_fp + total_local_fp)
            overall_metrics[1] = self.compute_recall(
                total_tp, total_fn + total_class_fp)
            overall_metrics[2] = self.compute_accuracy(
                total_tp, total_class_fp + total_local_fp, total_fn)
        return overall_metrics
    
    def get_class_metrics(self, label_data, iou_threshold, score_threshold):
        """
        Returns the precision, recall, and accuracy metrics and the truth \
            values of a specific class at the set IoU and score thresholds.

        Parameters
        ----------
            label_data: DetectionLabelData
                This is a container of the truth values of a specific class.

            iou_threshold:
                This is the IoU threshold for which to consider true positives.

            score_threshold:
                This is the score threshold for which to consider predictions.

        Returns
        -------
            class_metrics: np.ndarray (1, 3)
                This contains the values for precision, recall, and accuracy
                of the class representing the label data container.

            class_truth_values: np.ndarray (1, 4)
                This contains the values for true positives, classification
                false positives, localization false positives, and
                false negatives for the class representing the label data
                container. 

        Raises
        ------
            DivisionByZeroException
                Raised if a ZeroDivisionError occurs.

            ValueError
                Raised if the provided parameters for tp and fp
                are not integers or the values for tp and fp
                are negative integers.
        """
        iou_threshold = self.validate_threshold(iou_threshold)
        score_threshold = self.validate_threshold(score_threshold)
        # These are the truth values just for the specified class in the 
        # data container: true positives, false positives, and false negatives.
        tp = label_data.get_tp_count(
            iou_threshold, score_threshold)
        cfp = label_data.get_class_fp_count(
            iou_threshold, score_threshold)
        lfp = label_data.get_local_fp_count(
            iou_threshold, score_threshold)
        fn = label_data.get_fn_count(
            iou_threshold, score_threshold)

        class_metrics = np.zeros(3)
        class_truth_values = np.array([tp, cfp, lfp, fn])
        if tp == 0:
            if cfp + lfp == 0:
                class_metrics[0] = np.nan
            if fn == 0:
                class_metrics[1] = np.nan
            if cfp + lfp + fn == 0:
                class_metrics[2] = np.nan
        else:
            class_metrics[0] = self.compute_precision(tp, cfp + lfp)
            class_metrics[1] = self.compute_recall(tp, fn)
            class_metrics[2] = self.compute_accuracy(tp, cfp + lfp, fn)

        return class_metrics, class_truth_values

    def get_mean_average_metrics(self, validation_iou, score_threshold):
        """
        Returns the mean average precision, \
            recall, and accuracy for the iou thresholds [0.5, 0.75, 0.5-0.95].

            1. mean average precision = (sum of precision for every label) / \
                                (total number of unique labels).
            2. mean average recall = (sum of recall for every label) / \
                                (total number of unique labels).
            3. mean average accuracy = (sum of accuracy for every label) / \
                                (total number of unique labels).

        Also returns the data needed to plot the class histogram.

        Parameters
        ----------
            validation_iou: float
                The validation IoU threshold to consider true positives.

            score_threshold: float
                The validation score threshold to consider for predictions.

        Returns
        -------
            class metrics: list
                This contains mean average precision, recall, and accuracy
                at IoU threshold 0.5, 0.75, and 0.5-0.95.

            class histogram data: dict
                This contains the number of true positives,
                false positives, and false negatives and
                aswell as precision, recall, and accuracy at
                the set validation IoU threshold to plot as a histogram.

        Raises
        ------
            DivisionByZeroException
                Raised if a division of zero is encountered when 
                calculating precision, recall, or accuracy.

            ValueError
                Raised if the provided parameters for tp and fp
                are not integers or the values for tp and fp
                are negative integers.
        """
        validation_iou = self.validate_threshold(validation_iou)
        score_threshold = self.validate_threshold(score_threshold)
        class_histogram_data = dict()
        nc = len(self.detectiondatacollection.label_data_list)
        if nc == 0:
            class_histogram_data["No labels"] = {
                        'precision': np.nan,
                        'recall'   : np.nan,
                        'accuracy' : np.nan,
                        'tp': 0,
                        'fn': 0,
                        'fp': 0,
                        'gt': 0
            }
            return [[np.nan,np.nan,np.nan],
                    [np.nan,np.nan,np.nan],
                    [np.nan,np.nan,np.nan]], \
                    class_histogram_data
        else:
            # These arrays contain the metrics for each class where the rows
            # represent the class and the columns represent the IoU thresholds:
            # 0.00 to 1.00 in 0.05 intervals. 
            map_array, mar_array, macc_array = \
                np.zeros((nc, 20)), np.zeros((nc, 20)), np.zeros((nc, 20))
            
            for ic, label_data in enumerate(
                    self.detectiondatacollection.label_data_list):
                class_metrics, class_truth_values = self.get_class_metrics(
                    label_data, validation_iou, score_threshold)
                
                class_histogram_data[str(label_data.get_label())] = {
                        'precision': class_metrics[0],
                        'recall'   : class_metrics[1],
                        'accuracy' : class_metrics[2],
                        'tp': class_truth_values[0],
                        'fn': class_truth_values[3],
                        'fp': class_truth_values[1] + class_truth_values[2],
                        'gt': label_data.get_gt()
                    }
                
                for it, iou_threshold in enumerate(np.arange(0.00, 1, 0.05)):
                    class_metrics, _ = self.get_class_metrics(
                            label_data, iou_threshold, score_threshold)
                    # The index of the class ic and the index of the IoU
                    # threshold it will contain the metric: precision, recall,
                    # and accuracy of the class. 
                    map_array[ic][it] = class_metrics[0]
                    mar_array[ic][it] = class_metrics[1]
                    macc_array[ic][it] = class_metrics[2]
        
        # These arrays are essentially the mAP, mAR, and mACC across the 
        # IoU thresholds 0.00 to 1.00 in 0.05 intervals with shape (1, 20).
        if np.isnan(map_array).all():
            map_array = np.empty(20) * np.nan 
        else:
            map_array = np.nansum(map_array, axis=0) / nc  
        if np.isnan(mar_array).all():
            mar_array = np.empty(20) * np.nan 
        else:
            mar_array = np.nansum(mar_array, axis=0) / nc 
        if np.isnan(macc_array).all():
            macc_array = np.empty(20) * np.nan 
        else:
            macc_array = np.nansum(macc_array, axis=0) / nc      

        # These are the mAP, mAR, and mACC 0.5-0.95 IoU thresholds.
        map_5095, mar_5095, macc_5095 = \
            np.sum(map_array[10:])  / 10, \
            np.sum(mar_array[10:])  / 10, \
            np.sum(macc_array[10:]) / 10
        
        # This list contains mAP, mAR, mACC 0.50, 0.75, and 0.5-0.95.
        metric_map, metric_mar, metric_maccuracy = [
            map_array[10], map_array[15], map_5095], [
            mar_array[10], mar_array[15], mar_5095], [
            macc_array[10], macc_array[15], macc_5095]

        return [metric_map, metric_mar, metric_maccuracy], class_histogram_data

    def single_evaluation(self, score_threshold):
        """
        This is used for the precision-recall curve which will \
            run through each score threshold and performs the validator \
                evaluation based on the filtered detections. \
                
        Parameters
        ----------
            score_threshold: float
                The score threshold to filter the predictions.

        Returns
        -------
            None

        Raises
        ------
            MatchingAlgorithmException
                Raised if duplicate matches were found in the final results or
                an invalid metric is passed.

            ValueError
                Raised if the provided iou or score does not conform 
                to the specified data type or the parameters are 
                out of bounds. i.e. The provided iou or score is 
                greater than 1 or less than 0.
        """
        score_threshold = self.validate_threshold(score_threshold)
        # Reset the data.
        self.detectiondatacollection.reset_containers()
        instances = self.detectiondatacollection.get_instances()

        for _, instance in instances.items():
            gt_instance = instance.get("gt_instance")
            dt_instance = instance.get("dt_instance")

            # Filter detections only for valid scores based on threshold.
            dt_boxes, dt_labels, scores = filter_dt(
                dt_instance.get('boxes'), 
                dt_instance.get('labels'), 
                dt_instance.get('scores'), 
                score_threshold)
            instance['dt_instance']['boxes'] = dt_boxes
            instance['dt_instance']['labels'] = dt_labels
            instance['dt_instance']['scores'] = scores

            if self.clamp_box:
                instance = clamp_boxes(instance, self.clamp_box)
            if self.ignore_box:
                instance = ignore_boxes(instance, self.ignore_box)

            # Match ground truths to detections.
            self.detectiondatacollection.capture_class(
                dt_instance.get('labels'))
            self.detectiondatacollection.capture_class(
                gt_instance.get('labels'))

            if len(gt_instance.get('boxes')):            
                gt_boxes = np.append(
                    gt_instance.get('boxes'), 
                    np.expand_dims(gt_instance.get('labels'), axis=1), 
                    axis=1)
            else:
                gt_boxes = list()
            
            if len(dt_instance.get('boxes')):
                dt_boxes = np.append(
                    dt_instance.get('boxes'),
                    np.expand_dims(dt_instance.get('labels'), axis=1),
                    axis=1)
            else:
                dt_boxes = list()

            stats = match_gt_dt(
                gt_boxes, 
                dt_boxes,
                self.metric
            )
            # Evaluate.
            self.detectiondatacollection.categorize_simple(
                *stats,
                gt_labels=gt_instance.get('labels'),
                dt_labels=dt_instance.get('labels'),
                scores=dt_instance.get('scores'))
    
    def get_pr_data(
        self,
        score_threshold=0.5,
        iou_threshold=0.5,
        eps=1e-16,
        interval=0.01
        ):
        """
        Computes the precision and recall based on \
            varying score thresholds.

        Parameters
        ----------
            score_threshold: float
                The score threshold to consider for displaying the 
                average precision value on the plot. 

            iou_threshold: float
                The IoU threshold to consider true positives.

            eps: float
                Minimum value to substitute for zero.

            interval: float
                Score threshold interval to test
                from eps (min)...1. + interval (max)

        Returns
        -------
            data for plots:
                precision, recall, names.

        Raises
        ------
            ZeroUniqueLabelsException
                Raised if the number of unique labels captured is zero.

            DivisionByZeroException
                Raised if a division of zero is encountered \
                    when calculating precision and recall.
        """
        iou_threshold = self.validate_threshold(iou_threshold)
        score_threshold = self.validate_threshold(score_threshold)
        # The labels captured based on the dataset labels.txt.
        if len(self.detectiondatacollection.dataset_labels) == 0:
            # The labels captured based on the validation iterations. 
            if len(self.detectiondatacollection.get_labels()) == 0:
                raise ZeroUniqueLabelsException()
            else:
                all_labels = self.detectiondatacollection.labels
                nc = len(all_labels)
        else:
            all_labels = self.detectiondatacollection.dataset_labels
            if "background" in all_labels:
                all_labels = [
                    label for label in all_labels if label != "background"]
            nc = len(all_labels)
        
        score_min, score_max = eps, 1. + interval
        score_thresholds = np.arange(score_min, score_max, interval)

        # Precision and recall, rows = classes, columns = range of thresholds.
        # The extra two lengths are for the assertion of values of 1. 
        p = np.zeros((nc, len(score_thresholds)+2))
        r = np.zeros((nc, len(score_thresholds)+2))
        # Assert the last value for precision is 1 and the first value for 
        # recall is 1. 
        p[:, -1], r[:, 0] = 1, 1
        # Average Precision, rows = classes, columns = range of IoUs (0.5-0.95)
        ap = np.zeros((nc, 10))
        
        # Iterate the range of thresholds
        for ti, score_t in enumerate(score_thresholds):
            self.single_evaluation(score_t)
            
            # Precision for each class at this threshold.
            class_precision, class_recall = np.zeros(nc), np.zeros(nc)
           
            # Iterate through each data and grab precision and recall
            for label_data in self.detectiondatacollection.label_data_list:

                class_metrics, _ = self.get_class_metrics(
                    label_data, iou_threshold, score_t)

                # The index to store the precision and recall based on class
                current_label = label_data.get_label()
                if isinstance(current_label, (int, np.integer)):
                    current_label = all_labels[current_label]
                ci = all_labels.index(current_label)
                class_precision[ci] = class_metrics[0]
                class_recall[ci] = class_metrics[1]

                if round(score_t, 2) == round(score_threshold, 2):
                    # AP from recall-precision curve
                    ap[ci, :] = self.compute_ap_iou(
                        label_data, score_threshold)
            
            # Due to the assertion of the values of 1 for precision and recall,
            # the actual threshold starts at the offset of 1. 
            p[:, ti+1] = class_precision
            r[:, ti+1] = class_recall

        # This portion replaces NaN values with the last acceptable values.
        # This is necessary so that the lengths are the same for both 
        # precision and recall. 
        for ci in range(nc):
            p[ci] = nan_to_last_num(p[ci])
            r[ci] = nan_to_last_num(r[ci])

        return {
            "precision": p,
            "recall": r,
            "average precision": ap,
            "names": all_labels
        }

    def compute_ap_iou(self, label_data, score_threshold):
        """
        Computes the precision for a specific class \
            at 10 different iou thresholds.

        Parameters
        ----------
            label_data: DetectionLabelData
                A container for the number of tp, fp, and fn for the label.

            score_threshold: float
                The score threshold to consider for predictions.

        Returns
        -------
            precision: np.ndarray
                precision values for each IoU threshold (0.5-0.95).

        Raises
        ------
            ValueError
                Raised if the provided score_threshold 
                is not a floating point type and is out 
                bounds meaning it is greater than 1 or less than 0.

            DivisionByZeroException
                Raised if a division by zero occurs when \
                    calculating the precision.
        """
        score_threshold = self.validate_threshold(score_threshold)
        precision_list = np.zeros(10)
        for i, iou_threshold in enumerate(np.arange(0.5, 1, 0.05)):
            tp = label_data.get_tp_count(iou_threshold, score_threshold)
            class_fp = label_data.get_class_fp_count(
                iou_threshold, score_threshold)
            local_fp = label_data.get_local_fp_count(
                iou_threshold, score_threshold)
            if tp != 0:
                precision_list[i] = self.compute_precision(
                        tp, class_fp + local_fp)
        return precision_list

    def get_fp_error(self, score_threshold):
        """
        Calculates the false positive error ratios:: \

            1. Localization FP Error = Localization FP / \
                                (Classification FP + Localization FP).
            2. Classification FP Error = Classification FP / \
                                (Classification FP + Localization FP).

        *Note: localization false positives are predictions \
            that do no correlate to a ground truth. Classification \
                false positives are predictions with non matching labels.*
        
        Parameters
        ----------
            score_threshold: float
                The score threshold to consider for predictions.

        Returns
        -------
            Error Ratios: list
                This contains false positive ratios for
                IoU thresholds (0.5, 0.75, 0.5-0.95).

        Raises
        ------
            ValueError
                Raised if the provided score_threshold is
                not a floating point type and is out
                bounds meaning it is greater than 1 or less than 0.

            DivisionByZeroException
                Raised if a division by zero occurs when 
                calculating the error ratios.
        """
        score_threshold = self.validate_threshold(score_threshold)
        local_fp_error, class_fp_error = np.zeros(10), np.zeros(10)
        for it, iou_threshold in enumerate(np.arange(0.5, 1, 0.05)):
            _, _, \
                class_fp, local_fp = \
                    self.detectiondatacollection.sum_outcomes(
                    iou_threshold, score_threshold)
            if local_fp == 0 and class_fp == 0:
                local_fp_error[it] = np.nan
                class_fp_error[it] = np.nan
            else:
                local_fp_error[it] = self.divisor(
                    local_fp, local_fp + class_fp)
                class_fp_error[it] = self.divisor(
                    class_fp, local_fp + class_fp)
        return [local_fp_error[0], class_fp_error[0],
                local_fp_error[5], class_fp_error[5],
                np.sum(local_fp_error) / 10, np.sum(class_fp_error) / 10]