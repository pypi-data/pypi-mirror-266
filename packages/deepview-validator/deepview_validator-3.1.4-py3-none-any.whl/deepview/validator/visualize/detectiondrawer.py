# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.visualize.core import Drawer
from PIL import Image, ImageDraw, ImageFont

class DetectionDrawer(Drawer):
    """
    Provides methods to draw detection visualizations \
        such as bounding boxes.
    
    Parameters
    ----------
        None

    Raises
    ------
        None
    """
    def __init__(self):
        super(DetectionDrawer, self).__init__()

        self.texts = {
            "Match": "%s %.2f%% %.2f",
            "Match Loc": "LOC: %s %.2f%% %.2f",
            "Loc": "LOC: %s %.2f%%",
            "Clf": "CLF: %s %.2f%% %.2f"
        }

    @staticmethod
    def __drawRect(image_draw, color, text, textpos, boxpos):
        """
        Draws bouding boxes and texts on the image.
        
        Parameters
        ----------
            image_draw: PIL ImageDraw object
                The image to draw on.

            color: str
                Name to color the bounding box.

            text: str
                Text to describe the bounding box.

            testpos: tuple
                (x, y) position of the text.

            boxpos: tuple
                ((x1, y1), (x2, y2)) position of the box.

        Returns
        -------
            None

        Raises
        -------
            None
        """
        font = ImageFont.load_default()

        if hasattr(font, 'getsize'): # works on older Pillow versions < 10.
            text_width, text_height = font.getsize(text)
        else:
            (text_width, text_height), _ = font.font.getsize(text) # newer Pillow versions >= 10.

        box_text_x1 = boxpos[0][0]
        box_text_x2 = box_text_x1 + text_width

        if textpos[1] > boxpos[0][1]:
            box_text_y1 = boxpos[1][1] - text_height
        else:
            box_text_y1 = boxpos[0][1] 
            textpos = (textpos[0], textpos[1] + 10)

        box_text_y2 = box_text_y1 + text_height

        image_draw.rectangle(
            boxpos,
            outline=color,
            width=2)
        image_draw.rectangle(
            [(box_text_x1, box_text_y1), (box_text_x2, box_text_y2)],
            fill=color)
        image_draw.text(
            textpos,
            text,
            font=font,
            align='left',
            fill="black")
        
    @staticmethod
    def get_p1_p2(box, width, height):
        """
        Returns two tuple representing the coordinates of the
        bounding box corners.

        Parameters
        ----------
            box: list or np.darray
                This contains [xmin, ymin, xmax, ymax].

            width: int
                This is the width of the frame.

            height: int
                This is the height of the frame.

        Returns
        -------
            p1: tuple
                (xmin, ymin) Non-normalized coordinates.

            p2: tuple
                (xmax, ymax) Non-normalized coordinates.

        Raises
        ------
            None
        """
        p1 = (float(box[0]) * width, float(box[1]) * height)
        p2 = (float(box[2]) * width, float(box[3]) * height)
        return p1, p2

    def draw_with_pillow(
            self,
            iou_t,
            score_t,
            nimage,
            instance,
            matches,
            extras,
            _,
            iou_list
        ):
        """
        Draws detection bounding boxes and texts on the image \
            with distinct colors.

            1. RoyalBlue = ground truth or false negatives.
            2. LimeGreen = true positives.
            3. OrangeRed = false positives.

        Parameters
        ----------
            iou_t: float
                The validation IoU threshold between 0 and 1.

            score_t: float
                The validation score threshold between 0 and 1.

            nimage: (H, W, 3) np.ndarray
                Image represented as an numpy array.

            instance: dict
                This yields one image instance from the ground
                truth and the model predictions.
                See README.md (Method Parameters Format) for more information.

            matches: np.ndarray or list
                This contains the indices of matches
                [[index_dt, index_gt], ...].

            extras: np.ndarray or list
                This contains indices of extra predictions (local FP).

            iou_list: np.ndarray or list
                This contains IoU values of each match in respective order.

        Returns
        -------
            images: PIL image
                The image with drawn bounding boxes and text.

        Raises
        ------
            None
        """
        image = Image.fromarray(nimage)
        image_draw = ImageDraw.Draw(image)
        width = instance.get('gt_instance').get('width')
        height = instance.get('gt_instance').get('height')
       
        # Draw Ground Truths
        for label, box in zip(
            instance.get('gt_instance').get('labels'),
            instance.get('gt_instance').get('boxes')): 

            p1, p2 = self.get_p1_p2(box, width, height)
            self.__drawRect(image_draw, "RoyalBlue",
                            str(label), (p1[0], p2[1] - 12), (p1, p2))
            
        # Draw Extra Predictions
        for extra_index in extras:
            dt_label = instance.get('dt_instance').get('labels')[extra_index]
            box = instance.get('dt_instance').get('boxes')[extra_index]
            score = instance.get('dt_instance').get('scores')[extra_index]*100

            text = self.texts["Loc"] % (dt_label, score)
            p1, p2 = self.get_p1_p2(box, width, height)
            if score >= score_t*100:
                self.__drawRect(image_draw, "OrangeRed", text,
                                (p1[0], p1[1] - 10), (p1, p2))

        # Draw Predictions
        for match in matches:
            dt_label = instance.get('dt_instance').get('labels')[match[0]]
            gt_label = instance.get('gt_instance').get('labels')[match[1]]
            box = instance.get('dt_instance').get('boxes')[match[0]]
            iou = iou_list[match[0]]
            score =instance.get('dt_instance').get('scores')[match[0]]*100

            p1, p2 = self.get_p1_p2(box, width, height)
            if dt_label == gt_label:
                text = self.texts["Match"] % (dt_label, score, iou)
                if float(iou) >= iou_t:
                    color = "LimeGreen"
                else:
                    color = "OrangeRed"
            else:
                text = self.texts["Clf"] % (dt_label, score, iou)
                color = "OrangeRed"

            if score >= score_t*100:
                if iou < iou_t:
                    text = self.texts["Match Loc"] % (dt_label, score, iou)
                    self.__drawRect(image_draw, "OrangeRed", text,
                                    (p1[0], p1[1] - 10), (p1, p2))
                else:
                    self.__drawRect(image_draw, color, text,
                                (p1[0], p1[1] - 10), (p1, p2))
        return image