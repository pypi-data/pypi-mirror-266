# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.visualize.core import Drawer
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class SegmentationDrawer(Drawer):
    """
    Provides methods for drawing segmentation masks on the image.
    
    Parameters
    ----------
        None

    Raises
    -------
        None
    """
    def __init__(self):
        super(SegmentationDrawer, self).__init__()

    @staticmethod
    def polygon2maskimage(original_image, dt_polygon_list, gt_polygon_list):
        """
        Masks the original image and returns the masked image \
            with mask predictions on the left and ground truth \
                masks on the right. 
    
        Parameters
        ----------
            original_image: PIL Image object
                The original image opened using pillow.image.

            dt_polygon_list: list
                A list of predictions with polygon vertices
                [ [cls, x1, y1, x2, y2, x3, y3, ...] ...].

            gt_polygon_list: list
                A list of ground truth with polygon vertices
                [ [cls, x1, y1, x2, y2, x3, y3, ...] ...].

        Returns
        -------
            image: PIL image object
                The image with drawn mask where the left
                pane shows the ground truth mask and the right pane shows the
                prediction mask.

        Raises
        ------
            None
        """
        image_dt = original_image.convert("RGBA")
        new_dt = Image.new('RGBA', image_dt.size, (255, 255, 255, 0))
        img_dt = ImageDraw.Draw(new_dt)

        image_gt = original_image.convert("RGBA")
        new_gt = Image.new('RGBA', image_gt.size, (255, 255, 255, 0))
        img_gt = ImageDraw.Draw(new_gt)

        for dt_polygon in dt_polygon_list:
            img_dt.polygon(dt_polygon, fill=(255, 0, 0, 125))
            out_dt = Image.alpha_composite(image_dt, new_dt)

        for gt_polygon in gt_polygon_list:
            img_gt.polygon(gt_polygon, fill=(0, 0, 255, 125))
            out_gt = Image.alpha_composite(image_gt, new_gt)

        out_dt = out_dt.convert("RGB")
        out_gt = out_gt.convert("RGB")
        dst = Image.new('RGB', (out_dt.width + out_gt.width, out_dt.height))
        dst.paste(out_dt, (0, 0))
        dst.paste(out_gt, (out_dt.width, 0))
        return dst

    @staticmethod
    def mask2imagetransform(mask, labels, union=False):
        """
        Transform a numpy array of mask into an RGBA image.
        
        Parameter
        ---------
            mask: (height, width, 3) np.ndarray
                Array representing the mask.

            labels: list
                The list of prediction labels in the mask.

            union: bool
                Specify to mask all objects with one color (True).
                False otherwise.

        Returns
        -------
            image: PIL Image object
                The mask image.

        Raises
        ------
            None
        """
        colors = np.array([
                [180, 0, 0],
                [178, 179, 0],
                [142, 206, 70],
                [127, 96, 166],
                [2, 1, 181],
                [3, 152, 133],
                [121, 121, 121],
                [76, 0, 0],
                [240, 0, 0],
                [107, 123, 61],
                [245, 185, 0],
                [94, 78, 127],
                [202, 2, 202],
                [105, 153, 199],
                [252, 155, 209],
                [53, 76, 32],
                [146, 76, 17],
                [0, 166, 76],
                [0, 219, 99],
                [2, 71, 128]
            ], np.uint8)

        # Transform dimension of masks from a 2D numpy array to 4D with RGBA
        # channels
        mask_4_channels = np.stack((mask,) * 4, axis=-1)

        if union:
            # Assign all classes with color white
            mask_4_channels[mask_4_channels == 1] = 255
            # Temporarily unpack the bands for readability
            red, green, blue, _ = mask_4_channels.T
            # Areas of all classes
            u_areas = (red == 255) & (blue == 255) & (green == 255)
            # Color all classes with blue
            mask_4_channels[..., :][u_areas.T] = (0, 0, 255, 130)

        else:
            labels = np.sort(np.unique(labels))
            for label in labels:
                if label != 0:
                    # Designate a color for each class
                    mask_4_channels[mask_4_channels == label] = \
                        colors[label][0]
            
            # Temporarily unpack the bands for readability
            red, green, blue, _ = mask_4_channels.T
            for label in labels:
                if label != 0:
                    # Find object areas ... (leaves alpha values alone...)
                    object_areas = (red == colors[label][0]) &\
                    (blue == colors[label][0]) & (green == colors[label][0])
                    # Transpose back needed
                    # Color person objects with blue
                    mask_4_channels[..., :][object_areas.T] = \
                        np.append(colors[label], 130)
            
        # Convert array to image object for image processing
        return Image.fromarray(mask_4_channels.astype(np.uint8))

    def maskimage(self, image, instances):
        """
        Masks the original image and returns the original image \
            with mask prediction on the left and mask \
                ground truth on the right.
        
        Parameters
        ----------
            instances: dict
                This contains information such as ground truht and detection.
                See README.md (Method Parameters Format) for more information.

        Returns
        -------
            image: PIL Image object
                The image with drawn masks where on the right pane
                shows the ground truth mask and on the left pane shows
                the prediction mask.

        Raises
        ------
            None
        """
        original_image = Image.fromarray(np.uint8(image))
        dt_mask = instances.get('dt_instance').get('dt_mask')
        dt_labels = instances.get('dt_instance').get('labels')
        # Convert array to image object for image processing
        dt_im2 = self.mask2imagetransform(
            dt_mask, dt_labels)
        # convert img to RGBA mode
        image_dt = original_image.convert("RGBA")     
        out_dt = Image.alpha_composite(image_dt, dt_im2)
        out_dt = out_dt.convert("RGB")

        dst = Image.new('RGB', (out_dt.width, out_dt.height))
        dst.paste(out_dt, (0, 0))
        return dst

    def mask2maskimage(self, instances):
        """
        Masks the original image and returns the original image \
            with mask prediction on the left and mask \
                ground truth on the right.
        
        Parameters
        ----------
            instances: dict
                This contains information such as ground truht and detection.
                See README.md (Method Parameters Format) for more information.

        Returns
        -------
            image: PIL Image object
                The image with drawn masks where on the right pane
                shows the ground truth mask and on the left pane shows
                the prediction mask.

        Raises
        ------
            None
        """
        font = ImageFont.load_default()
        image = instances.get('gt_instance').get('image')
        original_image = Image.fromarray(np.uint8(image))

        gt_mask = instances.get('gt_instance').get('gt_mask')
        dt_mask = instances.get('dt_instance').get('dt_mask')
        gt_labels = instances.get('gt_instance').get('labels')
        dt_labels = instances.get('dt_instance').get('labels')

        # Convert array to image object for image processing
        gt_im2 = self.mask2imagetransform(
            gt_mask, gt_labels)
        dt_im2 = self.mask2imagetransform(
            dt_mask, dt_labels)

        # convert img to RGBA mode
        image_gt = original_image.convert("RGBA")
        image_dt = original_image.convert("RGBA")

        out_gt = Image.alpha_composite(image_gt, gt_im2)
        out_gt = out_gt.convert("RGB")
        
        out_dt = Image.alpha_composite(image_dt, dt_im2)
        out_dt = out_dt.convert("RGB")

        dst = Image.new('RGB', (out_dt.width + out_gt.width, out_dt.height))
        dst.paste(out_gt, (0, 0))
        dst.paste(out_dt, (out_dt.width, 0))

        drawtext = ImageDraw.Draw(dst)
        drawtext.text((0, 0), "GROUND TRUTH", font=font,
                      align='left', fill=(0, 0, 0))
        drawtext.text((out_dt.width, 0), "MODEL PREDICTION",
                      font=font, align='left', fill=(0, 0, 0))
        return dst

    def mask2mask4panes(
            self,
            instances,
            tp_mask,
            fp_mask,
            fn_mask
        ):
        """
        Creates a four pane image result:: \

            1. The first pane shows the masks for ground truth.
            2. Second pane shows masks for the model prediction.
            3. Third pane shows masks for the union of ground truth and \
                    model prediction.
            4. Fourth pane shows masks for tp, fp, fn.

        - For the first and second panes, person (blue) and car (red).
        - For the third pane, the union mask (blue).
        - For the last pane, the true positives, person (blue) car (red), \
            false negatives and false positives, person (light-blue), \
                car (light-red).

        Parameters
        ----------
            instances: dict
                This contains information regarding ground truth and 
                detection.
                See README.md (Method Parameters Format) for more information.

            tp_mask: (height, width) np.ndarray
                2D numpy array with the same size as the image and
                each element represents a pixel containing all true positives.

            fp_mask: (height, width) np.ndarray
                2D numpy array with the same size as the image and
                each element represents a pixel containing all false positives.

            fn_mask: (height, width) np.ndarray
                2D numpy array with the same size as the image and
                each element represents a pixel containing all false negatives.

        Returns
        -------
            image: PIL Image object
                The image with drawn masks panes.

        Raises
        ------
            None
        """
        font = ImageFont.load_default()
        image = instances.get('gt_instance').get('image')
        original_image = Image.fromarray(np.uint8(image))

        gt_mask = instances.get('gt_instance').get('gt_mask')
        dt_mask = instances.get('dt_instance').get('dt_mask')
        gt_labels = instances.get('gt_instance').get('labels')
        dt_labels = instances.get('dt_instance').get('labels')

        union_mask = np.add(dt_mask, gt_mask)
        union_mask = np.where(union_mask > 0, 1, union_mask)

        # Convert array to image object for image processing
        gt_im2 = self.mask2imagetransform(
            gt_mask, gt_labels)
        dt_im2 = self.mask2imagetransform(
            dt_mask, dt_labels)
        tp_im2 = self.mask2imagetransform(
            tp_mask, dt_labels)
        fp_im2 = self.mask2imagetransform(
            fp_mask, dt_labels)
        fn_im2 = self.mask2imagetransform(
            fn_mask, gt_labels)
        u_im2 = self.mask2imagetransform(
            union_mask, gt_labels+dt_labels, 
            union=True)

        # convert img to RGBA mode
        image_gt = original_image.convert("RGBA")
        image_dt = original_image.convert("RGBA")
        image_union = original_image.convert("RGBA")
        image_separate = original_image.convert("RGBA")

        out_gt = Image.alpha_composite(image_gt, gt_im2).convert("RGB")
        out_dt = Image.alpha_composite(image_dt, dt_im2).convert("RGB")
        out_union = Image.alpha_composite(image_union, u_im2).convert("RGB")
        out_sep1 = Image.alpha_composite(image_separate, tp_im2)
        out_sep2 = Image.alpha_composite(out_sep1, fp_im2)
        out_sep3 = Image.alpha_composite(out_sep2, fn_im2).convert("RGB")

        dst = Image.new('RGB', (out_dt.width + out_gt.width,
                        out_dt.height + out_gt.height))
        dst.paste(out_gt, (0, 0))
        dst.paste(out_dt, (out_dt.width, 0))
        dst.paste(out_union, (0, out_dt.height))
        dst.paste(out_sep3, (out_dt.width, out_dt.height))

        drawtext = ImageDraw.Draw(dst)
        drawtext.text((0, 0), "GROUND TRUTH", font=font,
                      align='left', fill=(0, 0, 0))
        drawtext.text((out_dt.width, 0), "MODEL PREDICTION",
                      font=font, align='left', fill=(0, 0, 0))
        drawtext.text((0, out_dt.height), "GT U DT",
                      font=font, align='left', fill=(0, 0, 0))
        drawtext.text(
            (out_dt.width,
             out_dt.height),
            "TP (Blue/Red), FP/FN(Light Blue/Red)",
            font=font,
            align='left',
            fill=(0,0,0))
        return dst