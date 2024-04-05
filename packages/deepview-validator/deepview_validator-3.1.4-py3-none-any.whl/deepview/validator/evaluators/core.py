# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.writers import ConsoleWriter, TensorBoardWriter
from datetime import datetime
import numpy as np
import json
import os

class Evaluator:
    """
    Abstract class that provides a template for the
        validation evaluations (detection or segmentation).
    
    Parameters
    ----------
        runner: Runner object depending on the model.
            This object provides methods to run the detection model.

        dataset: Dataset object depending on the dataset.
            This object provides methods to read and parse the dataset.

        visualize: str
            This is the path to store the images with visualizations. Can
            optionally be None to exclude.

        tensorboard: str
            This is the path to store the tensorboard tfevents file. Can
            optionally be None to exclude.

        json_out: str
            This is the path to the store the JSON file validation
            summary.

        display: int
            This is the number of images to save. By default it is -1
            specifying all the images.

        parameters: dict
            The model parameters:

                .. code-block:: python

                    {
                        "validation-iou": Validation IoU threshold,
                        "detection-iou": Detection NMS IoU threshold,
                        "validation-threshold": Validation score threshold,
                        "detection-threshold": Detection NMS score threshold,
                        "nms": NMS type,
                        "normalization": Image normalization to perform,
                        "maximum_detections": Max detections per image,
                        "warmup": number of model pre-warmups to perform,
                        "label offset": Label offset for the label index,
                        "metric": The metric to use to perform dt to gt match,
                        "clamp boxes": Dimension to clamp for smaller bbxs,
                        "ignore boxes": Minimum dimension allowable 
                    }

    Raises
    ------
        ValueError
            Raised if the parameter --json_out recieved an 
            extension that is not a json file.
    """
    def __init__(
        self,
        runner,
        dataset=None,
        visualize=None,
        tensorboard=None,
        json_out=None,
        display=-1,
        parameters=None
    ):
        self.runner = runner
        self.dataset = dataset
        self.visualize = visualize
        self.tensorboard = tensorboard
        self.display = display
        self.parameters = parameters
        self.counter = 0

        # Time of test => Used to name the test results folder.
        today = datetime.now().strftime('%Y-%m-%d--%H:%M:%S').replace(":", "_")
        self.json_out = json_out
        if json_out:
            if os.path.splitext(json_out)[1].lower() == ".json":
                if not os.path.exists(os.path.dirname(json_out)):
                    os.makedirs(os.path.dirname(json_out))
                self.json_out = json_out
            elif os.path.splitext(json_out)[1].lower() == "":
                if not os.path.exists(os.path.normpath(json_out)):
                    os.makedirs(os.path.normpath(json_out))
                self.json_out = os.path.join(json_out, "results.json")
            else:
                raise ValueError(
                    "--json_out parameter can only create " + 
                    "json files, but received {}".format(json_out))

        if visualize:
            self.save_path = os.path.join(
                visualize, 
                f"{os.path.basename(os.path.normpath(self.runner.source))}_{today}")
            if not os.path.exists(self.save_path):
               os.makedirs(self.save_path)
            self.consolewriter = ConsoleWriter()
            self.tensorboardwriter = None

        elif tensorboard:
            self.save_path = os.path.join(
                tensorboard, 
                f"{os.path.basename(os.path.normpath(self.runner.source))}_{today}")
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            self.tensorboardwriter = TensorBoardWriter(self.save_path)

        else:
            self.consolewriter = ConsoleWriter()
            self.tensorboardwriter = None

    def instance_collector(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method")

    def single_evaluation(self, instance, epoch, add_image):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method")

    def group_evaluation(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method")

    def conclude(self):
        """Abstract Method"""
        raise NotImplementedError("This is an abstract method")

    def print_types(self, d, tabs=0):
        """
        Debugs the typing of a data structure that the application 
        is trying to serialize into a JSON file.

        Parameters
        ----------
            d: dict or list
                This is the datastructure to debug for the types.

            tabs: int
                This allows for better formatting showing the nested
                structures.
        
        Returns
        -------
            None
        
        Raises
        ------
            None
        """
        if type(d) == type(dict()):
            for key, value in d.items():
                t = '\t'*tabs
                print(f"{t} {key=}: type: {type(value)}")
                if type(value) == type(dict()) or type(value) == type(list()):
                    self.print_types(value, tabs+1)
        elif type(d) == type(list()):
            for index in range(min(len(d), 4)):
                t = '\t'*tabs
                print(f"{t} {index=}: type: {type(d[index])}")
                if type(d[index]) == type(dict()) or \
                            type(d[index]) == type(list()):
                    self.print_types(d[index], tabs+1)

    def save_metrics_disk(
        self, 
        header, 
        format_summary, 
        format_timings,
        path=None
    ):
        """
        Saves the validation metrics onto a text file on disk.

        Parameters
        ----------
            header: str
                The title of the validation metrics.

            format_summary: str
                The formatted validation showing the metrics.

            format_timings: str
                The formatted timings summary.
            path: str
                This path will be used to alternatively store the metrics

        Returns
        -------
            None

        Raises
        ------
            None
        """
        
        with open(
            os.path.join(
                path if path else os.path.join(self.save_path, 'metrics.txt')
            ), 'w'
        ) as fp:
            fp.write(header + '\n')
            fp.write(format_summary + '\n')
            if format_timings is not None:
                fp.write(format_timings)
            fp.close()

    def publish_metrics(self, summary, epoch=0, validation_type="detection"):
        """
        Publishes the metrics onto tensorboard.

        Parameters
        ----------
            summary: dict
                The validation summary.
                See README.md (Method Parameters Format) for more information.

            epoch: int
                The epoch number when training a model.

            validation_type: str
                The type of validation that is being performed:
                "detection", "segmentation", "pose"

        Returns
        -------
            None

        Raises
        ------
            None 
        """
        header, summary, timings = self.tensorboardwriter.publish_metrics(
                        message=summary,
                        parameters=self.parameters,
                        step=epoch,
                        validation_type=validation_type)
        return header, summary, timings
        
class NpEncoder(json.JSONEncoder):
    """
    Encodes numpy arrays in the summary to be JSON serializable.
    The source for this class was retrieved from:: \
        https://stackoverflow.com/questions/50916422/\
            python-typeerror-object-of-type-int64-is-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)