# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.metrics.segmentationutils import create_mask_image, \
    create_mask_class, create_mask_background, classify_mask, \
    create_mask_classes
from deepview.validator.visualize.utils import plot_classification, \
    figure2numpy, close_figures
from deepview.validator.metrics import SegmentationDataCollection, \
    SegmentationMetrics
from deepview.validator.visualize import SegmentationDrawer
from deepview.validator.evaluators.core import Evaluator
from deepview.validator.datasets.core import Dataset
from os import path
import numpy as np

class SegmentationEval(Evaluator):
    """
    Provides methods to perform segmentation validation.
    The common process of running validation::

        1. Grab the ground truth and the model prediction instances per image.
        2. Create masks for both ground truth and model prediction.
        3. Classify the mask pixels as either tp, fp, or fn.
        4. Overlay the ground truth and predictions masks on the image.
        5. Calculate the metrics.

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
            The model parameters.
            See README.md (Method Parameters Format) for more information.
            This does not apply to segmentation, therefore it is set as None.

    Raises
    -------
        ValueError
            Raised if the provided parameters in certain methods 
            does not conform to the specified data type or the 
            parameters are out of bounds. i.e. The thresholds 
            provided are greater than 1 or less than 0.
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
        super(SegmentationEval, self).__init__(
            runner=runner,
            dataset=dataset,
            visualize=visualize,
            tensorboard=tensorboard,
            json_out=json_out,
            display=display,
            parameters=parameters
        )
        self.drawer = SegmentationDrawer()

    def __call__(self, labels=None, val_messenger=None):
        """
        Allows tensorboardformatter object in trainer to operate here \
        and resets the metrics after each epoch.
        Default validation has no use of this method.
        
        Parameters
        ----------
            labels: list or np.ndarray
                This list contains unique string labels for the classes found.

            val_messenger: TrainingTensorBoardWriter
                This object is internal for modelpack that was instantiated
                specifically for training a model.

        Returns
        -------
            None

        Raises
        ------
            None
        """
        if val_messenger is not None:
            self.tensorboardwriter = val_messenger
        self.datacollection = SegmentationDataCollection()
        self.labels = labels

    def instance_collector(self):
        """
        Instances are data containers that show information regarding the
        ground truth (image, height, width, boxes, labels, image path, gt_mask)
        model predictions (dt_mask, dt_labels)
        for each image.

        Collects the instances from the ground truth
        and the model segmentations.
        
        Parameters
        ----------
            None

        Returns
        -------
            instances: dict
                This yields one image instance from the ground
                truth and the model predictions.
                See README.md (Method Parameters Format) for more information.

        Raises
        ------
            None
        """
        for gt_instance in self.dataset.read_all_samples():

            # This is for gray images that can't be processed.
            if gt_instance is None:
                continue    
            height = gt_instance.get('height')
            width = gt_instance.get('width')

            gt_mask = create_mask_image(height, width, gt_instance)
            gt_instance['gt_mask'] = gt_mask
            gt_labels = np.unique(gt_mask)
            gt_instance['labels'] = gt_labels
            if path.splitext(self.runner.source)[1].lower() != "":
                image = gt_instance.get("image")
            else:
                image = gt_instance.get("image_path")
            dt_mask = self.runner.run_single_instance(image)
            dt_labels = np.unique(dt_mask)
            dt_instance = {
                'dt_mask': dt_mask,
                'labels': dt_labels
            }

            yield {
                'dt_instance': dt_instance,
                'gt_instance': gt_instance
            }

    def single_evaluation(self, instance, epoch=0, add_image=False):
        """
        Runs validation on a single instance.

        Parameters
        ----------
            instance: dict
                The ground truth and the predictions instances.
                See README.md (Method Parameters Format) for more information.

            epoch: int
                This is the training epoch number. This
                parameter is internal for modelpack usage.
                Default validation has no use of this parameter.

            add_image: bool
                If set to True, this will draw on the image
                with bounding boxes.

        Returns
        -------
            truth values: int
                total_tp, total_fn, total_class_fp, total_local_fp

        Raises
        ------
            None
        """
        height = instance.get('gt_instance').get('height')
        width = instance.get('gt_instance').get('width')
        self.drawer = SegmentationDrawer()
        gt_labels = instance.get('gt_instance').get('labels')
        dt_labels = instance.get('dt_instance').get('labels')
        class_labels = np.unique(gt_labels + dt_labels)

        self.datacollection.capture_class(class_labels, self.labels)

        gt_mask = instance.get('gt_instance').get('gt_mask')
        dt_mask = instance.get('dt_instance').get('dt_mask')
        dt_mask = Dataset.resize(dt_mask, (height, width))
        instance['dt_instance']['dt_mask'] = dt_mask
        cu_tp_mask, cu_fp_mask, cu_fn_mask = None, None, None

        for cl in class_labels:
            gt_class_mask = create_mask_class(gt_mask, cl)
            dt_class_mask = create_mask_class(dt_mask, cl)
            # Evaluate background class
            if cl == 0:
                gt_class_mask = create_mask_background(gt_mask)
                dt_class_mask = create_mask_background(dt_mask)

            tp, fp, fn, tp_mask, fp_mask, fn_mask = classify_mask(
                height, gt_class_mask, dt_class_mask, dt_mask)

            cu_tp_mask = create_mask_classes(
                tp_mask, cl, cu_tp_mask)
            cu_fp_mask = create_mask_classes(
                fp_mask, cl, cu_fp_mask)
            cu_fn_mask = create_mask_classes(
                fn_mask, cl, cu_fn_mask)

            if self.labels is not None:
                datalabel = self.datacollection.get_label_data(self.labels[cl])
            else: 
                datalabel = self.datacollection.get_label_data(cl)
            datalabel.add_tp(tp)
            datalabel.add_fp(fp)
            datalabel.add_fn(fn)
            datalabel.add_gt(tp + fn)

        # Execute this code for four pane image results
        if add_image:
            # Execute this code for two pane image results
            dst = self.drawer.mask2maskimage(instance)
            # dst = self.drawer.mask2mask4panes(
            #     instance, cu_tp_mask, cu_fp_mask, cu_fn_mask)

            if self.visualize:
                n_path = path.join(self.save_path, path.basename(
                    instance.get('gt_instance').get('image_path')))
                dst.save(n_path)
            elif self.tensorboardwriter:
                self.tensorboardwriter(dst, instance.get(
                    'gt_instance').get('image_path'), step=epoch)
        return self.datacollection.sum_outcomes()

    def group_evaluation(self):
        """
        Performs the instance segmentation evaluation of all images.

        Parameters
        ----------
            None

        Returns
        -------
            truth values: int
                total_tp, total_fn, total_fp.

        Raises
        ------
            None
        """
        self.counter = 0
        self.datacollection=SegmentationDataCollection()

        for instance in self.instance_collector():

            gt_labels = instance.get('gt_instance').get('labels')
            dt_labels = instance.get('dt_instance').get('labels')
            # A ground truth with just background and detection with just 
            # background will result in True positives. Should avoid this.
            if len(gt_labels) == 1 and len(dt_labels) == 1:
                if gt_labels[0] == 0 and dt_labels[0] == 0:
                    continue
            class_labels = np.unique(np.append(gt_labels, dt_labels))

            self.datacollection.capture_class(
                class_labels, self.dataset.labels)

            height = instance.get('gt_instance').get('height')
            width = instance.get('gt_instance').get('width')
            gt_mask = instance.get('gt_instance').get('gt_mask')
            dt_mask = instance.get('dt_instance').get('dt_mask')
            dt_mask = Dataset.resize(dt_mask, (height, width))
            instance['dt_instance']['dt_mask'] = dt_mask
            cu_tp_mask, cu_fp_mask, cu_fn_mask = None, None, None

            for cl in class_labels:

                gt_class_mask = create_mask_class(gt_mask, cl)
                dt_class_mask = create_mask_class(dt_mask, cl)
                # Evaluate background class
                if cl == 0:
                    gt_class_mask = create_mask_background(gt_mask)
                    dt_class_mask = create_mask_background(dt_mask)

                tp, fp, fn, tp_mask, fp_mask, fn_mask = classify_mask(
                    height, gt_class_mask, dt_class_mask, dt_mask)

                cu_tp_mask = create_mask_classes(
                    tp_mask, cl, cu_tp_mask)
                cu_fp_mask = create_mask_classes(
                    fp_mask, cl, cu_fp_mask)
                cu_fn_mask = create_mask_classes(
                    fn_mask, cl, cu_fn_mask)

                datalabel = self.datacollection.get_label_data(
                    self.dataset.labels[cl])
                datalabel.add_tp(tp)
                datalabel.add_fp(fp)
                datalabel.add_fn(fn)
                datalabel.add_gt(tp + fn)

            # Execute this code for two pane image results
            dst = self.drawer.mask2maskimage(instance)

            # Execute this code for four pane image results
            # dst = self.drawer.mask2mask4panes(
            #    instance, cu_tp_mask, cu_fp_mask, cu_fn_mask)

            if self.display >= 0:
                if self.counter < self.display:
                    self.counter += 1
                else:
                    continue

            if self.visualize:
                n_path = path.join(self.save_path, path.basename(
                    instance.get('gt_instance').get('image_path')))
                dst.save(n_path)
            elif self.tensorboardwriter:
                self.tensorboardwriter(dst, instance.get(
                    'gt_instance').get('image_path'))
            else:
                continue
        return self.datacollection.sum_outcomes()

    def conclude(self, truth_values, epoch=0):
        """
        Computes the final metrics, draws the class histogram, and
        saves the results either to tensorboard or to the local machine.

        Parameters
        ----------
            truth values: int
                total_tp, total_fn, total_fp

            epoch: int
                This is the training epoch number. This
                parameter is internal for modelpack usage.
                Default validation has no use of this parameter.

        Returns
        -------
            summary: dict
                The validation summary
                See README.md (Method Parameters Format) for more information.

        Raises
        ------
            None
        """
        metrics = SegmentationMetrics(
            segmentationdatacollection=self.datacollection)
        
        if self.runner is not None:
            timings = self.runner.summarize()
            engine = self.runner.device
        else:
            timings = None
            engine = "cpu"

        if self.parameters is not None:
            self.parameters["engine"] = engine

        try:
            model_name = path.basename(self.runner.source)
        except AttributeError:
            model_name = "Training Model"

        try:
            dataset_name = path.basename(path.normpath(self.dataset.source))
        except AttributeError:
            dataset_name = "Validation Dataset"

        mean_metrics, class_histogram_data =\
              metrics.compute_segmentation_metrics()
        overall_metrics = metrics.compute_overall_metrics(*truth_values)

        summary = {
            "model": model_name,
            "engine": engine,
            "dataset": dataset_name,
            "numgt": int(self.datacollection.total_gt),
            "Total TP": truth_values[0],
            "Total FN": truth_values[1],
            "Total FP": truth_values[2],
            "OP": overall_metrics[0],
            "OR": overall_metrics[1],
            "OA": overall_metrics[2],
            "mAP": mean_metrics[0],
            "mAR": mean_metrics[1],
            "mACC": mean_metrics[2],
            "timings": timings
        }

        if self.visualize or self.tensorboardwriter:
            fig_class_metrics = plot_classification(
                class_histogram_data, model=model_name)

        if self.visualize:
            fig_class_metrics.savefig(
                f'{self.save_path}/class_scores.png',
                bbox_inches="tight")
            close_figures([fig_class_metrics])
        elif self.tensorboardwriter:
            nimage_class = figure2numpy(fig_class_metrics)
            self.tensorboardwriter(
                nimage_class,
                f"{summary.get('model')}_scores.png",
                step=epoch)
            close_figures([fig_class_metrics])
            
        if self.json_out:
            import json
            summary["class_histogram_data"] = class_histogram_data
            with open(self.json_out, 'w') as fp:
                json.dump(summary, fp)

        if self.tensorboardwriter:
            self.tensorboardwriter.publish_metrics(message=summary, 
                step=epoch, validation_type="segmentation")
        else:
            header, format_summary, format_timings = self.consolewriter(
                message=summary, validation_type="segmentation")

            if self.visualize:
                with open(self.save_path + '/metrics.txt', 'w') as fp:
                    fp.write(header + '\n')
                    fp.write(format_summary + '\n')
                    if timings is not None:
                        fp.write(format_timings)
                fp.close()

        # Resetting Containers
        self.datacollection = SegmentationDataCollection()
        return summary