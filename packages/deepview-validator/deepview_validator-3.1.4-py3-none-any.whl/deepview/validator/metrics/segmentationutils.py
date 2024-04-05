# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from PIL import Image, ImageDraw
import numpy as np

def validate_input_mask(mask):
    """
    Validates the input mask to be a numpy array.
    
    Parameters
    ----------
        mask: np.ndarray
            The mask to validate as a numpy array.

    Returns
    -------
        mask: np.ndarray
            The validated mask being a numpy array.

    Raises
    ------
        ValueError
            Raised Rif the input
            mask is not of type np.ndarray.
    """
    if not (isinstance(mask, np.ndarray)):
        raise ValueError("The input mask is not of type np.ndarray. " +
                         "Recieved type: {}".format(type(mask)))
    return mask

def create_mask_image(height, width, gt_instance):
    """
    Creates a numpy array of masks from a given polygon.
    
    Parameters
    ----------
        height: int
            The height of the image.

        width: int
            The width of the image.

        gt_instance: dict

            .. code-block:: python

                {
                    "image": (height, width, 3) np.ndarray representing
                            the image,
                    "height": image height,
                    "width": image width,
                    "segments": contains the polygons in each list,
                    "labels": contains string or int labels to
                            represent each polygon,
                    "image_path": the path to the image
                }

    Returns
    -------
        Masked image: (height, width) np.ndarray

    Raises
    ------
        ValueError
            Raised if gt_instance is not a
            dictionary and if the width and height are not integers
            or the dimensions of the width and height are invalid
            such as less than or equal to 0.
    """
    if not (isinstance(gt_instance, dict)):
        raise ValueError("The provided gt_instance is not a dictionary. " +
                         "Recieved {}".format(type(gt_instance)))
    elif not (isinstance(width, int) or isinstance(height, int)):
        raise ValueError(
            "The provided width and height are not integers. " +
            "Recieved width: {} and height {}.".format(
                type(width),
                type(height)))
    else:
        if (width <= 0 or height <= 0):
            raise ValueError(
                "The provided width and height have invalid dimensions. " +
                "Recieved width: {} and height: {}".format(
                    width,
                    height))
        else:
            gt_segments = gt_instance.get('segments')
            gt_labels = gt_instance.get('labels')

            img = Image.new('L', (width, height), 0)
            for c, polygon in zip(gt_labels, gt_segments):
                ImageDraw.Draw(img).polygon(
                    polygon, outline=int(c), fill=int(c))
            # This array contains a mask of the image where the objects are
            # outlined by class number
            mask = np.array(img)
            return mask

def create_binary_mask(mask):
    """
    Creates a binary numpy array of 1's and 0's \
        encapsulating every object (regardless of class) \
            in the image as a 1 and background as 0.
    
    Parameters
    ----------
        mask: (height, width) np.ndarray
            Mask of class labels unique to each object.

    Returns
    -------
        binary_mask: (height, width) np.ndarray
            Binary mask of 1's and 0's.

    Raises
    ------
        ValueError
            Raised if the input mask is not of type np.ndarray.
    """
    mask = validate_input_mask(mask)
    binary_mask = np.where(mask > 0, 1, mask)
    return binary_mask

def create_mask_class(mask, cls):
    """
    Separates a mask with more than one classes into \
        an individual mask of 1's and 0's where 1 represents the \
            specified class and 0 represents other classes.
    
    Parameters
    ----------
        mask: (height, width) np.ndarray
            Mask of class labels unique to each object.

        cls: int
            The integer representing the class in the mask
            to keep as a value of 1.

    Returns
    -------
        binary_mask: (height, width) np.ndarray
            Binary mask of 1's and 0's.

    Raises
    ------
        ValueError
            Raised if the input mask is not of type 
            np.ndarray or if the input cls is not of type Integer.
    """
    mask = validate_input_mask(mask)
    if not (isinstance(cls, (int, np.integer))):
        raise ValueError("The provided input parameter cls is not an integer. "
                         "Recieved type: {}".format(type(cls)))
    else:
        temp_mask = np.where(mask != cls, 0, mask)
        temp_mask[temp_mask == cls] = 1
        return temp_mask

def create_mask_classes(new_mask, cls, current_mask=None):
    """
    Appends a current mask with another mask of different \
        class i.e converting a binary mask (new mask) into \
            a mask with its class and then appending the \
                original mask to include the new mask with its class.
  
    Parameters
    ----------
        new_mask: (height, width) np.ndarray
            The current binary mask.

        cls: int
            Class representing the 1's in the new mask.

        current_mask: (height, width) np.ndarray
            Current multiclass mask.

    Returns
    -------
        multiclass mask: (height, width) np.ndarray
            Mask with an additional class added.

    Raises
    ------
        ValueError
            Raised if the input masks is not of type 
            np.ndarray or if the input cls is not of type Integer.
    """
    new_mask = validate_input_mask(new_mask)
    if current_mask is not None:
        current_mask = validate_input_mask(current_mask)

    if not (isinstance(cls, (int, np.integer))):
        raise ValueError("The provided input parameter cls is not an integer. "
                         "Recieved type: {}".format(type(cls)))
    else:
        new_mask = np.where(new_mask == 1, cls, new_mask)
        if current_mask is not None:
            return np.add(current_mask, new_mask)
        else:
            return new_mask

def create_mask_background(mask):
    """
    Creates a binary mask for the background class with ones \
        in the image and the rest of the objects will have values of zeroes.
    
    Parameters
    ----------
        mask: (height, width) np.ndarray
            Matrix array of classes representing the image pixels.

    Returns
    -------
        mask: (height, width) np.ndarray
            Binary mask of 1's and 0's, where 1's is background and
            objects are 0's

    Raises
    ------
        ValueError
            Raised if the input masks is not of type np.ndarray.
    """
    mask = validate_input_mask(mask)
    # 2 is a temporary class
    temp_mask = np.where(mask != 0, 2, mask)
    temp_mask[temp_mask == 0] = 1
    temp_mask[temp_mask == 2] = 0
    return temp_mask

def classify_mask(height, gt_class_mask, dt_class_mask, dt_mask):
    """
    Classifies if the pixel is either a true positive, \
        false positive, or a false negative.    
   
    Parameters
    ----------
        height: int
            The height of the model input shape.

        gt_class_mask: (height, width) np.ndarray
            2D binary array representing pixels forming the image ground truth.

        dt_class_mask: (height, width) np.ndarray
            2D binary array representing pixels forming the image prediction.

        dt_mask: (height, width) np.ndarray
            2D array containing all the classes forming the image prediction.

    Returns
    -------
        outcomes: int, (height, width) np.ndarray
            The number of tp, fp, fn, and the tp_mask, fp_mask, fn_mask.

    Raises
    ------
        ValueError
            Raised if the input masks is not of type 
            np.ndarray or if the input height is not of type 
            Integer or has invalid dimension.
    """
    gt_class_mask = validate_input_mask(gt_class_mask)
    dt_class_mask = validate_input_mask(dt_class_mask)
    dt_mask = validate_input_mask(dt_mask)

    if not (isinstance(height, int)):
        raise ValueError("The provided height is not of type integer. " +
                         "Recieved type: {}".format(type(height)))
    else:
        if (height <= 0):
            raise ValueError("The provided height has invalid dimensions. " +
                             "Recieved height: {}".format(height))
        else:
            # Create a binary mask of the prediction image encapsulating all
            # predicted objects
            p_image = create_binary_mask(dt_mask)
            p_image_flat = p_image.flatten()
            gt_mask_flat = gt_class_mask.flatten()
            dt_mask_flat = dt_class_mask.flatten()
            # Compute TP
            tp_mask = gt_mask_flat * dt_mask_flat
            tp_mask = np.reshape(tp_mask, (-1, height))
            tp = sum(gt_mask_flat * dt_mask_flat)
            # Compute FP
            # Swtich 0 as 1 and 1 as 0. In this case if gt is background and dt
            # is an object, it is a FP.
            gt_flat = np.logical_not(gt_mask_flat).astype(int)
            fp_mask = gt_flat * dt_mask_flat
            fp_mask = np.reshape(fp_mask, (-1, height))
            fp = sum(gt_flat * dt_mask_flat)
            # Compute FN
            # Swtich 0 as 1 and 1 as 0. In this case if dt is background and gt
            # is an object, it is a FN.
            dt_flat = np.logical_not(dt_mask_flat).astype(int)
            p_flat = np.logical_not(p_image_flat).astype(int)
            fn_mask = gt_mask_flat * dt_flat * p_flat
            fn_mask = np.reshape(fn_mask, (-1, height))
            fn = sum(gt_mask_flat * dt_flat * p_flat)
            return tp, fp, fn, tp_mask, fp_mask, fn_mask