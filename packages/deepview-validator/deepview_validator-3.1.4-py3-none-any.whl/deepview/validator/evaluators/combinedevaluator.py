from PIL import Image
import numpy as np

class CombinedEvaluator:

    def __init__(
        self,
        detectionevaluator=None,
        segmentationevaluator=None,
        poseevaluator=None
    ):
        self.detectionevaluator = detectionevaluator
        self.segmentationevaluator = segmentationevaluator
        self.poseevaluator = poseevaluator

    def __call__(self, labels=None, val_messenger=None):
        self.detectionevaluator(labels=labels, val_messenger=val_messenger)
        self.segmentationevaluator(labels=labels, val_messenger=val_messenger)
        self.tensorboardwriter = val_messenger

    def single_detection_evaluation(self, instance):
        truth_values = self.detectionevaluator.single_evaluation(instance)
        return truth_values

    def single_segmentation_evaluation(self, instance):
        truth_values = self.segmentationevaluator.single_evaluation(instance)
        return truth_values

    def single_pose_evaluation(self):
        pass

    def single_evaluation(self, detection_instance, segmentation_instance):
        detection_truth_values = self.detectionevaluator.single_evaluation(detection_instance)
        segmentation_truth_values = self.segmentationevaluator.single_evaluation(segmentation_instance)
        return detection_truth_values, segmentation_truth_values

    def publish_image(self, image, image_path, epoch, detection_instance, segmentation_instance):
        if self.tensorboardwriter:
            image = self.detectionevaluator.drawer.draw_with_pillow(
                self.detectionevaluator.parameters.get("validation-iou"), 
                self.detectionevaluator.parameters.get("validation-threshold"),
                image, 
                detection_instance, 
                *self.detectionevaluator.stats
            )
            image = self.segmentationevaluator.drawer.maskimage(image, segmentation_instance)

            if not isinstance(image, (np.ndarray, Image.Image)):
                image = np.asarray(image)
            self.tensorboardwriter(image, image_path, step=epoch)

    def conclude(self, det_truth_values, seg_truth_values):
        segmentation_metrics = self.segmentationevaluator.conclude(seg_truth_values, epoch=0)
        detection_metrics = self.detectionevaluator.conclude(det_truth_values, epoch=0)
        return detection_metrics, segmentation_metrics
        




    
