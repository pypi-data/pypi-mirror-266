# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.metrics.poseutils import crop_frame_bbxarea
from deepview.validator.metrics.posedata import PoseDataCollection
from deepview.validator.metrics.posemetrics import PoseMetrics
from deepview.validator.visualize.posedrawer import PoseDrawer
from deepview.validator.evaluators.core import Evaluator
from deepview.validator.datasets.core import Dataset
from deepview.validator.writers.core import Writer
from PIL import Image
from os import path
import numpy as np

class PoseEval(Evaluator):
    """
    Performs pose evaluation for headpose models.

    Parameters
    ----------
        runner: Runner object
            This provides methods for models to generate predictions.

        dataset: Dataset object
            This provides methods to read and parse a provided dataset.

        visualize: str
            The path to store images with visualizations.

        tensorboard: str
            The path to store the tfevents file that contain results of the
            validation.

        json_out: str
            The path to store a JSON file containing the validation summary.

        display: int
            The number of images to display or save on disk.

        parameters: dict
            The model parameters.
            See README.md (Method Parameters Format) for more information.
            This does not apply to pose, therefore it is set as None.

    Raises
    ------  
        None
    """
    def __init__(
            self, 
            runner=None, 
            dataset=None, 
            visualize=None, 
            tensorboard=None, 
            json_out=None, 
            display=-1, 
            parameters=None
        ):
        super(PoseEval, self).__init__(
            runner=runner, 
            dataset=dataset,
            visualize=visualize, 
            tensorboard=tensorboard, 
            json_out=json_out, 
            display=display, 
            parameters=parameters
        )
        self.drawer = PoseDrawer()

    def __call__(self, labels=None, val_messenger=None):
        """
        Allows tensorboardformatter object in trainer to operate here. 
        Also resets data container after each epoch.
        Default validation has no use of this method.

        Parameters
        ----------
            labels: str, default None
                This parameter is not used in this evaluator but it is included to keep aligned with rest of the evaluators
            val_messenger: TensorBoardWriter
                This object handles publishing of validation results
                to tensorboard.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        if val_messenger is not None:
            self.tensorboardwriter = val_messenger
        self.datacollection = PoseDataCollection()
        
    def instance_collector(self):
        """
        Collects the ground truth and the pose instances for \
            one image into a single dictionary.

        Parameters
        ----------
            None

        Returns
        -------
            instances: dict
                This yeilds a single image instance containing the 
                ground truth and the pose instances.
                See README.md (Method Parameters Format) for more information.

        Raises
        ------
            None
        """
        for gt_instance in self.dataset.read_all_samples():
            # This is for gray images that can't be processed.
            if gt_instance is None:
                continue
            
            if path.exists(gt_instance.get('image_path')):
                image = gt_instance.get('image_path')
            elif isinstance(gt_instance.get('image'), np.ndarray):
                image = gt_instance.get('image')
            else:
                raise ValueError(
                    "The provided image_path does not exist at: " +
                    gt_instance.get('image_path') +
                    "The provided image array is not a numpy.ndarray: " +
                    type(gt_instance.get('image'))
                )
            
            w, h = gt_instance.get("width"), gt_instance.get("height")
            # Denormalize boxes
            gt_instance["boxes"] = Dataset.denormalize(
                gt_instance.get("boxes"), h, w)
            # Currently boxes are stored in a list of list
            dt_instance = {
                "angles": [],
                "labels": []
            }
            gt_instance["angles"] = np.squeeze(gt_instance.get("angles"))
            if len(gt_instance.get("boxes")):
                gt_box = gt_instance.get("boxes")[0]
                gt_instance["boxes"] = gt_box
                if path.splitext(self.runner.source)[1].lower() != "":
                    image = crop_frame_bbxarea(image, gt_box)
                angles, labels = self.runner.run_single_instance(image)

                dt_instance = {
                    'angles': angles,
                    'labels': labels,
                    }
            yield {
                'gt_instance': gt_instance,
                'dt_instance': dt_instance
                }

    def single_evaluation(self, instance, epoch=0, add_image=False):
        """
        Performs a single image evaluation.
        
        Parameters
        ----------
            instance: dict
                A container for the ground truth and the pose instances.
                See README.md (Method Parameters Format) for more information.

            epoch: int
                Used for training a model the epoch number.

            add_image: bool
                If this is set to true it means to save the image or 
                display the image into tensorboard.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        gt_instance = instance.get("gt_instance")
        dt_instance = instance.get("dt_instance")

        dt_angles = dt_instance.get("angles")
        # Currently inside a list of lists
        gt_angles = gt_instance.get("angles")
        
        self.datacollection.store_angles(dt_angles, gt_angles)
        
        if add_image:
            if self.visualize or self.tensorboardwriter:
                original_image = instance.get('gt_instance').get('image')
                image = self.drawer.draw_both_axis(
                    original_image, 
                    dt_angles, 
                    gt_angles,
                    gt_box=gt_instance.get('boxes')
                    )

            if self.visualize:
                image.save(path.join(self.save_path, path.basename(
                    instance.get('gt_instance').get('image_path'))))
            elif self.tensorboardwriter:
                nimage = np.asarray(image)
                self.tensorboardwriter(nimage, instance.get(
                    'gt_instance').get('image_path'), step=epoch)

    def group_evaluation(self):
        """
        Performs evaluation across the entire dataset.

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
        self.datacollection = PoseDataCollection()
        self.counter = 0
    
        for instances in self.instance_collector():
            gt_instance = instances.get("gt_instance")
            dt_instance = instances.get("dt_instance")

            if None in [gt_instance, dt_instance]:
                Writer.logger(
                    "Ground truth and detection instances returned None. " +
                    "Contact support@au-zone.com for more information.", 
                    code="WARNING")
                break

            gt_angles = gt_instance.get("angles")
            dt_angles = dt_instance.get("angles")
            self.datacollection.store_angles(dt_angles, gt_angles)
            
            if self.visualize or self.tensorboardwriter:
                original_image = instances.get('gt_instance').get('image')
                if len(gt_instance.get("angles")):
                    image = self.drawer.draw_both_axis(
                        original_image, 
                        dt_angles, 
                        gt_angles, 
                        gt_box=instances.get('gt_instance').get('boxes'))
                else:
                    image = Image.fromarray(original_image)

                if self.display >= 0:
                    if self.counter < self.display:
                        self.counter += 1
                    else:
                        continue

            if self.visualize:
                image.save(path.join(self.save_path, path.basename(
                    instances.get('gt_instance').get('image_path'))))
            elif self.tensorboardwriter:
                nimage = np.asarray(image)
                self.tensorboardwriter(nimage, instances.get(
                    'gt_instance').get('image_path'))
            else:
                continue
        
    def conclude(self, epoch=0):
        """
        Gathers the final model metrics.
        
        Parameters
        ----------
            epoch: int
                This is used for training the epoch number.

        Returns
        -------
            summary: dict
                This contains the validation metrics.

        Raises
        ------
            None
        """
        metrics = PoseMetrics(self.datacollection)
        if self.runner is not None:
            timings = self.runner.summarize()
            device = self.runner.device
        else:
            timings = None
            device = "unknown"

        # Grab the validation metrics
        overall_metrics = metrics.compute_overall_metrics()

        # Contain the metrics inside a dictionary
        summary = self.create_summary(overall_metrics, timings)
        summary["engine"] = device

        if self.tensorboardwriter:
            self.publish_metrics(summary, epoch, validation_type="pose")
        else:
            header, format_summary, format_timings = self.consolewriter(
                message=summary,
                parameters=self.parameters,
                validation_type="pose")
            
            if self.visualize:
                self.save_metrics_disk(header, format_summary, format_timings) 

        # Resetting containers
        self.datacollection = PoseDataCollection()   
        return summary

    def create_summary(self, overall_metrics, timings):
        """
        Creates the summary dictionary containing the validation
        metrics for headpose.
            
        Parameters
        ----------
            overall_metrics: list
                This contains the mean squared error for roll, pitch, yaw.

            timings: dict
                This contains the timing information.
                See README.md (Method Parameters Format) for more information.

        Returns
        -------
            summary: dict
                The validation metrics.

        Raises
        ------
            None
        """
        try:
            model_name = path.basename(path.normpath(self.runner.source))
        except AttributeError:
            model_name = "Training Model"

        try:
            dataset_name = path.basename(path.normpath(self.dataset.source))
        except AttributeError:
            dataset_name = "Validation Dataset"

        if len(overall_metrics) == 3:
            metrics = {
                "roll": overall_metrics[0],
                "pitch": overall_metrics[1],
                "yaw": overall_metrics[2]
            }
        elif len(overall_metrics) == 4:
            metrics = {
                "real": overall_metrics[0],
                "i": overall_metrics[1],
                "j": overall_metrics[2],
                "k": overall_metrics[3]
            }
        else:
            metrics = dict()
            for i in range(len(overall_metrics)):
                metrics["angle_{}".format(1)] = overall_metrics[i]

        summary = {
            "model": model_name,
            "dataset": dataset_name,
            "timings": timings
        }
        summary.update(metrics)
        return summary