# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.visualize.core import Drawer
from PIL import Image, ImageDraw
import numpy as np

class PoseDrawer(Drawer):
    """
    Draws the axis for provided angles for roll, pitch, and yaw.

    Parameters
    ---------- 
        None

    Raises
    ------
        None
    """
    def __init__(self):
        super(Drawer, self).__init__()

    @staticmethod
    def draw_axis(
        image_draw, roll, pitch, yaw, tdx, tdy, colors, size=150, gt_box=None):
        """
        Draws the compass on the frame.

        Parameters
        ----------
            image_draw: PIL ImageDraw object
                The image to draw the compass on.

            roll: float
                The angle in degrees for roll.

            pitch: float
                The angle in degrees for pitch.

            yaw: float
                The angle in degrees for yaw.

            tdx: int
                The starting position of the lines.

            tdy: int
                The starting position of the lines.

            colors: tuple
                This contains the string colors to draw. 
                ("blue", "green", "red")  or any other combination for
                the three axis. 

            size: int
                The length of the lines.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        # X-Axis (out of the screen) drawn in red
        x1 = size * (np.sin(yaw)) + tdx
        y1 = size * (-np.cos(yaw) * np.sin(pitch)) + tdy
        # Y-Axis pointing to right. drawn in green
        x2 = size * (np.cos(yaw) * np.cos(roll)) + tdx
        y2 = size * (np.cos(pitch) * np.sin(roll) + np.cos(roll)
                    * np.sin(pitch) * np.sin(yaw)) + tdy
        # Z-Axis | drawn in blue
        x3 = size * (-np.cos(yaw) * np.sin(roll)) + tdx
        y3 = size * (np.cos(pitch) * np.cos(roll) - np.sin(pitch)
                    * np.sin(yaw) * np.sin(roll)) + tdy
        
        # This is to keep the rotations constant in one direction and 
        # avoid illusions of rotations going back and forth.
        if yaw >= (-80*np.pi/180) and yaw <= (170*np.pi/180):
            axis_behind = (int(x2), int(y2))
            axis_infront = (int(x1), int(y1))
            color_behind = colors[1]
            color_infront = colors[2]
        else:
            axis_behind = (int(x1), int(y1))
            axis_infront = (int(x2), int(y2))
            color_behind = colors[2]
            color_infront = colors[1]

        image_draw.line(
            (int(tdx),int(tdy), axis_behind[0], axis_behind[1]), 
            fill=color_behind, 
            width=5)
        image_draw.line(
            (int(tdx),int(tdy), int(x3), int(y3)), 
            fill=colors[0], 
            width=5)
        image_draw.line(
            (int(tdx),int(tdy), axis_infront[0], axis_infront[1]), 
            fill=color_infront, 
            width=5)

        if gt_box is not None:
            image_draw.rectangle(
                [(gt_box[0], gt_box[1]), (gt_box[2], gt_box[3])],
                outline="green",
                width=2)
    
    def draw_both_axis(
            self, nimage, dt_euler, gt_euler, tdx=None, tdy=None, gt_box=None):
        """
        Draws both the ground truth and the pose angles on the \
            same image with different colors.

        Parameters
        ----------
            nimage: np.ndarray
                The image to draw on.

            dt_euler: list
                This contains the model prediction roll, pitch, yaw in degrees.
            
            gt_euler: list
                This contains the ground truth roll, pitch, and yaw in degrees.

            tdx: int
                The starting position of the lines.

            tdy: int
                The starting position of the lines.

        Returns
        -------
            image: Pillow Image object
                The image with drawn axis.

        Raises
        ------
            None
        """
        if tdx is None or tdy is None:
            if gt_box is not None:
                x1, y1, x2, y2 = gt_box
                tdx = int((x1+x2)* 0.5)
                tdy = int((y1+y2)* 0.5)
            else:
                height, width = nimage.shape[:2]
                tdx = width / 2  
                tdy = height / 2
               
        image = Image.fromarray(nimage)
        image_draw = ImageDraw.Draw(image)
        if len(dt_euler):
            self.draw_axis(
                image_draw, 
                *dt_euler, 
                tdx=tdx, 
                tdy=tdy, 
                colors=("lightblue", "lightgreen", "tomato"))
        if len(gt_euler) and len(gt_box):
            self.draw_axis(
                image_draw, 
                *gt_euler, 
                tdx=tdx, 
                tdy=tdy, 
                colors=("blue", "green", "red"), 
                gt_box=gt_box)
        return image