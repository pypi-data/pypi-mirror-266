# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import MatchingAlgorithmException
from deepview.validator.exceptions import InvalidIoUException
from deepview.validator.writers import Writer
import numpy as np

def center_point_distance(box_a, box_b):
    """
    Finds the distance between the center of two \
        bounding boxes using pythagoras. 
    
    Parameters
    ----------
        boxA: list or np.ndarray
            This contains [xmin, ymin, xmax, ymax] for detections.

        boxB: list or np.ndarray
            This contains [xmin, ymin, xmax, ymax] for ground truth.

    Returns
    -------
        center point distance: float
            This is the distance from center to center of the
            bounding boxes.

    Raises
    ------
        None
    """
    width_a = box_a[2] - box_a[0]
    width_b = box_b[2] - box_b[0]
    height_a = box_a[3] - box_a[1]
    height_b = box_b[3] - box_b[1]

    a = abs((box_a[0] + width_a/2) - (box_b[0] + width_b/2))
    b = abs((box_a[1] + height_a/2) - (box_b[1] + height_b/2))
    return (a**2 + b**2)**0.5

def bb_intersection_over_union(box_a, box_b, eps=1e-10):
    """
    Computes the IoU between ground truth and detection \
        bounding boxes. IoU computation method retrieved from:: \
            https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
    
    Parameters
    ----------
        box_a: list
            This is a bounding box [xmin, ymin, xmax, ymax].
        
        box_b: list
            This is a bounding box [xmin, ymin, xmax, ymax].

    Returns
    -------
        IoU: float
            The IoU score between boxes.

    Exceptions
    ----------
        InvalidIoUException
            Raised if the calculated IoU is invalid. 
            i.e. less than 0 or greater than 1.

        ValueError
            Raised if the provided boxes for ground truth 
            and detection does not have a length of four.
    """
    if len(box_a) != 4 or len(box_b) != 4:
        raise ValueError("The provided bounding boxes does not meet " \
                            "expected lengths [xmin, ymin, xmax, ymax]")
    
    # determine the (x, y)-coordinates of the intersection rectangle
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    # compute the area of intersection rectangle
    inter_area = max((x_b - x_a, 0)) * max((y_b - y_a), 0)
    if inter_area == 0:
        return 0.
    # compute the area of both the prediction and ground-truth
    # rectangles
    box_a_area = abs((box_a[2] - box_a[0]) * (box_a[3] - box_a[1]))
    box_b_area = abs((box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = inter_area / float(box_a_area + box_b_area - inter_area)

    if iou > 1. + eps or iou < 0.:
        raise InvalidIoUException(iou)
    # return the intersection over union value
    return iou   

def filter_dt(boxes, classes, scores, threshold):
    """
    Filters the detections to include only scores \
        greater than or equal to the validation threshold set.
    
    Parameters
    ----------
        boxes: np.ndarray
            The prediction bounding boxes.. [[box1], [box2], ...].

        classes: np.ndarray
            The prediction labels.. [cl1, cl2, ...].

        scores: np.ndarray
            The prediction confidence scores.. [score, score, ...]
            normalized between 0 and 1.

        threshold: float
            This is the validation score threshold to filter
            the detections.

    Returns
    ------- 
        boxes, classes, scores: np.ndarray
            These contain only the detections whose scores are 
            larger than or greater than the validation threshold set.

    Raises
    ------
        None
    """
    filter_indices = range(len(classes))
    if isinstance(classes, np.ndarray): 
        if len(classes):
            if np.issubdtype(classes.dtype, np.integer):
                filter_indices = np.argwhere(scores>=threshold).flatten()
            elif classes.dtype.type is np.str_:
                filter_indices = np.argwhere(
                    (scores>=threshold) & (classes != "background")).flatten()
            else:
                raise ValueError("All elements in the classes numpy array " +
                                "must either be int or strings.")
    elif isinstance(classes, list):
        if len(classes):
            if all(isinstance(label, str) for label in classes):
                filter_indices = np.argwhere(
                    (scores>=threshold) & (classes != "background")).flatten()
            elif not all(isinstance(label, int) for label in classes):
                raise ValueError("All elements in the labels list " +
                                    "must either be strings or integers.")
    else:
        raise ValueError("labels can only be of type list or np.ndarray.")
    
    boxes = np.take(boxes, filter_indices, axis=0)
    scores = np.take(scores, filter_indices, axis=0)
    classes = np.take(classes, filter_indices, axis=0)
    return boxes, classes, scores

def clamp_boxes(instances, clamp):
    """
    Clamps bounding box less than the provided clamp value to \
        the clamp value in pixels. The minimum width and height \
            of the bounding is the clamp value in pixels. 
    
    Parameters
    ----------
        instances: dict
            This contains the ground truth and the detection data.
            See README.md (Method Parameters Format) for more information.

        clamp: int
            The minimum acceptable dimensions of the bounding boxes for 
            detections and ground truth. 

    Returns
    -------
        instances: dict
            This now contains the updated clamped bounding boxes.

    Raises
    ------ 
        None
    """
    height = instances.get('gt_instance').get('height')
    width = instances.get('gt_instance').get('width')
    gt_boxes = instances.get('gt_instance').get('boxes')
    dt_boxes = instances.get('dt_instance').get('boxes')

    gt_widths = ((gt_boxes[..., 2:3] - gt_boxes[..., 0:1])*width).flatten()
    gt_heights = ((gt_boxes[..., 3:4] - gt_boxes[..., 1:2])*height).flatten()
    dt_widths = ((dt_boxes[..., 2:3] - dt_boxes[..., 0:1])*width).flatten()
    dt_heights = ((dt_boxes[..., 3:4] - dt_boxes[..., 1:2])*height).flatten()

    gt_modify = np.transpose(
        np.nonzero(((gt_widths<clamp)+(gt_heights<clamp)))).flatten()
    dt_modify = np.transpose(
        np.nonzero(((dt_widths<clamp)+(dt_heights<clamp)))).flatten()
    if len(gt_boxes):
        gt_boxes[gt_modify, 2:3] = gt_boxes[gt_modify, 0:1] + clamp/width
        gt_boxes[gt_modify, 3:4] = gt_boxes[gt_modify, 1:2] + clamp/height
        instances['gt_instance']['boxes'] = gt_boxes
    if len(dt_boxes):
        dt_boxes[dt_modify, 2:3] = dt_boxes[dt_modify, 0:1] + clamp/width
        dt_boxes[dt_modify, 3:4] = dt_boxes[dt_modify, 1:2] + clamp/height
        instances['dt_instance']['boxes'] = dt_boxes
    return instances

def ignore_boxes(instances, ignore):
    """
    Ignores the boxes with dimensions less than the ignore \
        parameter provided. 
    
    Parameters
    ----------
        instances: dict
            This contains the ground truth and the detection data.
            See README.md (Method Parameters Format) for more information.

        ignore: int
            The dimension pixels threshold to ignore. Any boxes with width 
            and height less than this value will be ignored and filtered out.

    Returns
    -------
        instances: dict
            This is the updated instances data which filtered out the boxes.

    Raises
    ------
        None
    """
    height = instances.get('gt_instance').get('height')
    width = instances.get('gt_instance').get('width')
    gt_boxes = instances.get('gt_instance').get('boxes')
    gt_labels = instances.get('gt_instance').get('labels')  
    dt_boxes = instances.get('dt_instance').get('boxes')
    dt_labels = instances.get('dt_instance').get('labels')
    scores = instances.get('dt_instance').get('scores')

    gt_widths = ((gt_boxes[..., 2:3] - gt_boxes[..., 0:1])*width).flatten()
    gt_heights = ((gt_boxes[..., 3:4] - gt_boxes[..., 1:2])*height).flatten()
    dt_widths = ((dt_boxes[..., 2:3] - dt_boxes[..., 0:1])*width).flatten()
    dt_heights = ((dt_boxes[..., 3:4] - dt_boxes[..., 1:2])*height).flatten()

    gt_keep = np.transpose(
        np.nonzero(((gt_widths>=ignore)*(gt_heights>=ignore)))).flatten()
    dt_keep = np.transpose(
        np.nonzero(((dt_widths>=ignore)*(dt_heights>=ignore)))).flatten()
    
    gt_boxes = np.take(gt_boxes, gt_keep, axis=0)
    gt_labels =  np.take(gt_labels, gt_keep, axis=0)
    dt_boxes = np.take(dt_boxes, dt_keep, axis=0)
    dt_labels = np.take(dt_labels, dt_keep, axis=0)
    scores = np.take(scores, dt_keep, axis=0)

    instances['gt_instance']['boxes'] = gt_boxes
    instances['gt_instance']['labels'] = gt_labels
    instances['dt_instance']['boxes'] = dt_boxes
    instances['dt_instance']['labels'] = dt_labels
    instances['dt_instance']['scores'] = scores
    return instances

def nan_to_last_num(process_array):
    """
    Replaces all NAN values with the last valid number. If all \
        values are NaN, then all elements are replaced with zeros.
    
    Parameters
    ----------
        process_array: np.ndarray
            This is the array to replace NaN values with the last 
            acceptable value.

    Returns
    -------
        process_array: np.ndarray
            The same array but with NaN replaced with last acceptable values.
            Otherwise, all elements are replaced with zeros if all elements are
            NaN.

    Raises
    ------
        None
    """
    try:
        # Find the maximum index where the value is not a NaN.
        precision_repeat_id = np.max(
            np.argwhere(
                np.logical_not(
                    np.isnan(process_array))).flatten())
        # NaN values should be replace with the last acceptable value.
        process_array = np.nan_to_num(
            process_array,
            nan=process_array[int(precision_repeat_id)])
    except ValueError:
        # The whole array are nans just convert back to zero.
        process_array[np.isnan(process_array)] = 0.
    return process_array

def match_gt_dt(gt_boxes, dt_boxes, metric='iou'):
    """
    Version 2 of the matching algorithm which incorporates \
        recursive calls to perform rematching of ground truth that were \
            unmatched due to duplicative matches, but the rematching is based \
                on the next best IoU. 

    Parameters
    ----------
        gt_boxes: list or np.ndarray
            A list of ground truth boxes [[x1, y1, x2, y2]...].

        dt_boxes: list or np.ndarray
            A list of prediction boxes [[x1, y1, x2, y2]...].

    Returns
    -------
       indices : list
            This contains indices of the matches, extra predictions,
            missed ground truths, and IoU values for each match.

                * matches [[detection index, ground truth index],
                        [detection index, ground truth index], ...]
                * extras [detection index, detection index, ...]
                * missed [ground truth index, ground truth index, ...]

    Raises
    ------
        MatchingAlgorithmException
            Raised if duplicate matches were found in the final results or
            an invalid metric is passed.
    """
    # This contains the IoUs of each detection.
    iou_list = np.zeros(len(dt_boxes))
    # Row is ground truth, columns is detection IoUs
    iou_grid = np.zeros((len(gt_boxes), len(dt_boxes)))
    index_matches = list()

    def compare_matches(dti, gti, iou):
        """
        Checks if duplicate matches exists. A duplicate match \
            is when the same detection is being matched to more than one \
                ground truth. The IoUs are compared and the better IoU is \
                    the true match and the ground truth of the other match \
                        is then rematch to the next best IoU, but it performs \
                            a recursive call to check if the next best IoU \
                                also generates a duplicate match.

        Parameters
        ----------
            dti: int
                The detection index being matched to the current ground truth.
            
            gti: int
                The current ground truth matched to the detection.

            iou: float
                The current best IoU that was computed for the current ground
                truth against all detections.

        Returns
        -------
            None

        Raises
        ------
            MatchingAlgorithmException:
                Raised if a duplicate match was left unchecked 
                and was not rematched. 
        """
        twice_matched = [(d,g) for d, g in index_matches if d == dti]
        if len(twice_matched) == 1:
            # Compare the IoUs between duplicate matches.
            dti, pre_gti = twice_matched[0]
            if iou > iou_list[dti]:
                index_matches.remove((dti, pre_gti))
                iou_list[dti] = iou
                index_matches.append((dti, gti))

                # Rematch pre_gti
                iou_grid[pre_gti][dti] = 0.
                dti = np.argmax(iou_grid[pre_gti])
                iou = max(iou_grid[pre_gti])
                if iou > 0.:
                    compare_matches(dti, pre_gti, iou)
            else:
                # Rematch gti
                iou_grid[gti][dti] = 0.
                dti = np.argmax(iou_grid[gti])
                iou = max(iou_grid[gti])
                if iou > 0.:
                    compare_matches(dti, gti, iou)

        elif len(twice_matched) == 0:
            if iou > 0.:
                iou_list[dti] = iou
                index_matches.append((dti, gti))
        else:
            raise MatchingAlgorithmException(
                "Duplicate matches were unchecked.") 

    if len(gt_boxes) > 0:
        for gti, gt in enumerate(gt_boxes):
            # A list of prediction indices with matching labels 
            # as the ground truth.
            dti_reflective = list()
            iou_reflective = list()
            if len(dt_boxes):
                for dti, dt in enumerate(dt_boxes):
                    # Find the IoUs of each prediction against the current gt.
                    if metric.lower() == 'iou':
                        iou_grid[gti][dti] = \
                            bb_intersection_over_union(
                                dt[:4].astype(float), 
                                gt[:4].astype(float))
                    elif metric.lower() == 'centerpoint':
                        iou_grid[gti][dti] = \
                            1 - center_point_distance(
                                    dt[:4].astype(float), 
                                    gt[:4].astype(float))
                    else:
                        raise MatchingAlgorithmException("Unknown matching " + 
                                    "matching metric specified.")
                    if not (
                        isinstance(dt[4:5].item(), type(gt[4:5].item())) or 
                        isinstance(gt[4:5].item(), type(dt[4:5].item()))
                        ):
                        Writer.logger(
                            "The labels type are not matching. " +
                            "detection: {} is {} and ground truth: {} is {}"
                                .format(
                                    dt[4:5].item(), 
                                    type(dt[4:5].item()), 
                                    gt[4:5].item(), 
                                    type(gt[4:5].item())
                                ), 
                            code="WARNING")
                    if dt[4:5].item() == gt[4:5].item():
                        dti_reflective.append(dti)
                        iou_reflective.append(iou_grid[gti][dti])
            else:
                return [index_matches, [], list(range(0, len(gt_boxes))), []]
            
            # A potential match is the detection that produced the highest IoU.
            dti = np.argmax(iou_grid[gti])
            iou = max(iou_grid[gti])

            if len(dti_reflective) and dt_boxes[dti][4:5] != gt_boxes[gti][4:5]:
                # The IoU of the detections with the same labels 
                # as the ground truth. A potential match is the 
                # detection with the same label as the ground truth.
                dti = dti_reflective[np.argmax(iou_reflective)]
                iou = max(iou_reflective)  
            compare_matches(dti, gti, iou)
               
        # Find the unmatched predictions
        index_unmatched_dt = list(range(0, len(dt_boxes)))
        index_unmatched_gt = list(range(0, len(gt_boxes)))
        for match in index_matches:
            index_unmatched_dt.remove(match[0])
            index_unmatched_gt.remove(match[1])                    
    else:
        index_unmatched_dt = list(range(0, len(dt_boxes)))
        index_unmatched_gt = list()
    return [index_matches, index_unmatched_dt, index_unmatched_gt, iou_list]