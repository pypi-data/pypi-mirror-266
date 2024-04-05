# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from PIL import Image
import numpy as np
import os

def crop_frame_bbxarea(image, gt_box):
    """
    Crops the frame to include only the bounding box that \
        surrounds the helmet or the head for pose validation.
    
    Parameters
    ----------
        image: np.ndarry
            The frame to crop before feeding to the model.

        gt_box: list or np.ndarray
            This contains [xmin, ymin, xmax, ymax].

    Returns
    -------
        box_area: np.ndarray
            The frame cropped to the area of the bounding box. 

    Raises
    ------
        None
    """

    if isinstance(image, str):
        if os.path.exists(image):
            image = np.asarray(Image.open(image))
        else:
            raise ValueError(
                "The given image path does not exist at {}".format(
                    image))

    x1, y1, x2, y2  = gt_box
    box_area = image[y1:y2, x1:x2, ...]
    return box_area