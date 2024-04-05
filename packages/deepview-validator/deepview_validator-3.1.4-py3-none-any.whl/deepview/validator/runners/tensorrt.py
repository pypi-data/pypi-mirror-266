# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import NonMatchingIndexException
from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.runners.core import Runner
from time import monotonic_ns as clock_now
from os.path import exists
from PIL import Image
import numpy as np

class TensorRTRunner(Runner):
    """
    Runs TensorRT Engines (.trt).

    Parameters
    ----------
        engine_path: str
            The path to the TensorRT engine.

        labels: list
            Unique string labels.

        preprocessor: str
            Specify the preprocessor of the engine.
            (EfficientDet, ...)

        detection_score_threshold: float
            NMS score threshold from 0 to 1.

        label_offset: int
            The index offset to match label index to the ground truth index.

    Raises
    ------
        MissingLibraryException
            Raised if the tensorrt and pycuda library
            is not installed.

        NonMatchingIndexException
                Raised if the model outputs an index
                that is out of bounds to the labels list passed.

        ValueError
            Raised if the provided image is not a
            string path pointing to the image or if the provided path does
            not exist.
    """
    def __init__(
        self,
        engine_path,
        labels,
        preprocessor="EfficientDet",
        detection_score_threshold=0.5,
        label_offset=0
    ):
        super(TensorRTRunner, self).__init__(engine_path)

        try:
            import tensorrt as trt
        except ImportError:
            raise MissingLibraryException(
                "tensorrt is needed to allow running of tensorRT engines.")

        try:
            import pycuda.driver as cuda
        except ImportError:
            raise MissingLibraryException(
                "pycuda driver is needed to perform memory allocations.")

        # Use autoprimaryctx if available (pycuda >= 2021.1) to
        # prevent issues with other modules that rely on the primary
        # device context.
        try:
            import pycuda.autoprimaryctx
        except ModuleNotFoundError:
            try:
                import pycuda.autoinit
            except ImportError:
                raise MissingLibraryException(
                    "supported NVIDIA GPU device is needed.")

        self.score_threshold = detection_score_threshold
        self.labels = labels
        self.preprocessor = preprocessor
        self.device = 'GPU'
        self.label_offset = label_offset

        # Load TRT engine
        self.logger = trt.Logger(trt.Logger.ERROR)
        trt.init_libnvinfer_plugins(self.logger, namespace="")

        with open(engine_path, "rb") as f, trt.Runtime(self.logger) as runtime:
            assert runtime
            self.engine = runtime.deserialize_cuda_engine(f.read())
        assert self.engine
        self.context = self.engine.create_execution_context()
        assert self.context

        # Setup I/O bindings
        self.inputs, self.outputs, self.allocations = list(), list(), list()

        for i in range(self.engine.num_bindings):

            is_input = False
            if self.engine.binding_is_input(i):
                is_input = True
            name = self.engine.get_binding_name(i)
            dtype = np.dtype(trt.nptype(self.engine.get_binding_dtype(i)))
            shape = self.context.get_binding_shape(i)

            if is_input and shape[0] < 0:
                assert self.engine.num_optimization_profiles > 0
                profile_shape = self.engine.get_profile_shape(0, name)
                assert len(profile_shape) == 3  # min,opt,max
                # Set the *max* profile as binding shape
                self.context.set_binding_shape(i, profile_shape[2])
                shape = self.context.get_binding_shape(i)

            if is_input:
                self.batch_size = 1
            size = dtype.itemsize

            for s in shape:
                size *= s

            allocation = cuda.mem_alloc(size)
            host_allocation = None if is_input else np.zeros(shape, dtype)

            binding = {
                "index": i,
                "name": name,
                "dtype": dtype,
                "shape": list(shape),
                "allocation": allocation,
                "host_allocation": host_allocation,
            }

            self.allocations.append(allocation)
            if self.engine.binding_is_input(i):
                self.inputs.append(binding)
            else:
                self.outputs.append(binding)

        assert self.batch_size > 0
        assert len(self.inputs) > 0
        assert len(self.outputs) > 0
        assert len(self.allocations) > 0

        self.shape = self.inputs[0]['shape']
        self.dtype = self.inputs[0]['dtype']
        self.format = None
        self.width, self.height = -1, -1

        if self.shape[1] == 3:
            self.format = "NCHW"
            self.height = self.shape[2]
            self.width = self.shape[3]
        elif self.shape[3] == 3:
            self.format = "NHWC"
            self.height = self.shape[1]
            self.width = self.shape[2]
        assert all([self.format, self.width > 0, self.height > 0])

    def infer(self, batch):
        """
        Executes inference on a batch of images.

        Parameters
        ----------
            batch: np.ndarray

        Returns
        -------
            

        Raises
        ------
            MissingLibraryException
                Raised if the pycuda library is not installed.
        """
        try:
            import pycuda.driver as cuda
        except ImportError:
            raise MissingLibraryException(
                "pycuda driver is needed to generate inference.")

        # Copy I/O and Execute
        cuda.memcpy_htod(self.inputs[0]['allocation'], batch)
        self.context.execute_v2(self.allocations)
        for o in range(len(self.outputs)):
            cuda.memcpy_dtoh(
                self.outputs[o]['host_allocation'],
                self.outputs[o]['allocation'])
        return [o['host_allocation'] for o in self.outputs]

    def run_single_instance(self, image):
        """
        Executes inference on a batch of images.
        The images should already be batched and preprocessed, \
            as prepared by the ImageBatcher class. Memory copying to \
                and from the GPU device be performed here.
    
        Parameters
        ----------
            image: str
                The path to the image to feed the engine.

        Returns
        -------
            boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            ValueError
                Raised if the provided image is not a
                string path pointing to the image or if the provided path does
                not exist.
        """
        if isinstance(image, str):
            start = clock_now()
            if exists(image):
                image, img_scale, img_dim = self.preprocess_input(image)
            else:
                raise ValueError(
                    "The provided image path does not exist at: {}".format(
                        image))
            load_ns = clock_now() - start
        else:
            raise ValueError(
                "The provided image is not a string path that points " +
                "to the image. Provided with type: {}".format(type(image)))
        self.loading_input_timings.append(load_ns * 1e-6)

        start = clock_now()
        outputs = self.infer(image)
        infer_ns = clock_now() - start
        self.inference_timings.append(infer_ns * 1e-6)

        start = clock_now()
        boxes, classes, scores = self.postprocessing(
            outputs, img_scale, *img_dim)
        boxes_ns = clock_now() - start
        self.box_timings.append(boxes_ns * 1e-6)
        return boxes, classes, scores

    def resize_pad(self, image, pad_color=(0, 0, 0)):
        """
        A subroutine to implement padding and resizing.
        This resize the image to fit fully within the input \
            size, and pads the remaining bottom-right portions with \
                the value provided.

        Parameters
        ----------
            image: PIL object
                image to resize.

            pad_color: tuple
                The RGB values to use for the padded area.
                Default: Black/Zeros.

        Returns
        -------
            pad: PIL object
                The PIL image object already padded and cropped.

            scale: int
                resize scale used.

            width: int
                The width of the original image.

            height: int
                The height of the original image.

        Raises
        ------
            None
        """
        width, height = image.size
        width_scale = width / self.width
        height_scale = height / self.height
        scale = 1.0 / max(width_scale, height_scale)
        image = image.resize(
            (round(width * scale),round(height * scale)),
            resample=Image.BILINEAR)
        pad = Image.new("RGB", (self.width, self.height))
        pad.paste(pad_color, [0, 0, self.width, self.height])
        pad.paste(image)
        return pad, scale, width, height

    def preprocess_input(self, image_path):
        """
        Uses the image preprocessor which loads an image from disk \
            and prepares it as needed for batching. This includes padding, \
                resizing, normalization, data type casting, and transposing.
        This Image Batcher implements one algorithm for now:: \
            * EfficientDet: Resizes and pads the image to fit the input size.

        Parameters
        ----------
            image_path: str
                The path to the image to load from disk.

        Returns
        -------
            image: np.ndarray
                A numpy array holding the image sample.

            scale: int
                resize scale used.

            (width, height): tuple
                represents the image dimensions.

        Raises
        ------
            None
        """
        scale = None
        image = Image.open(image_path)
        image = image.convert(mode="RGB")

        if self.preprocessor == "EfficientDet":
            # For EfficientNet V2: Resize & Pad with ImageNet mean values and
            # keep as [0,255] Normalization
            image, scale, width, height = self.resize_pad(
                image, (124, 116, 104))
            image = np.asarray(image, dtype=self.dtype)
            # [0-1] Normalization, Mean subtraction and Std Dev
            # scaling are part of the EfficientDet graph, so
            # no need to do it during preprocessing here
        else:
            print("Preprocessing method {} not supported".format(
                    self.preprocessor))
            exit(1)
        if self.format == "NCHW":
            image = np.transpose(image, (2, 0, 1))
        return image, scale, (width, height)

    def postprocessing(self, outputs, img_scale, width, height):
        """
        Processing the prediction outputs to parse the \
            detection bounding boxes, classes and scores.

        Parameters
        ----------
            outputs:

            img_scale:

            width: int
                The width of the image.

            height: int
                The height of the image.

        Returns
        -------
             boxes: np.ndarray
                The prediction bounding boxes.. [[box1], [box2], ...].

            classes: np.ndarray
                The prediction labels.. [cl1, cl2, ...].

            scores: np.ndarray
                The prediction confidence scores.. [score, score, ...]
                normalized between 0 and 1.

        Raises
        ------
            NonMatchingIndexException
                Raised if the model outputs an index
                that is out of bounds to the labels list passed.
        """
        # Process the results
        nums = outputs[0]
        boxes, scores, classes = outputs[1], outputs[2], outputs[3]
        normalized = (np.max(boxes) < 2.0)
        nmsed_boxes, nmsed_classes, nmsed_scores = list(), list(), list()

        for n in range(int(nums[0])):
            scale = self.inputs[0]['shape'][2] if normalized else 1.0

            if img_scale:
                scale /= img_scale
            if scores[0][n] < self.score_threshold:
                continue

            nmsed_boxes.append([(boxes[0][n][1] * scale) / width,
                                (boxes[0][n][0] * scale) / height,
                                (boxes[0][n][3] * scale) / width,
                                (boxes[0][n][2] * scale) / height])

            label = int(classes[0][n]) + self.label_offset

            if len(self.labels):
                try:
                    nmsed_classes.append(self.labels[label])
                except IndexError:
                    raise NonMatchingIndexException(label)
            else:
                nmsed_classes.append(label)
            nmsed_scores.append(scores[0][n])

        return np.array(nmsed_boxes), np.array(
            nmsed_classes), np.array(nmsed_scores)

    def input_spec(self):
        """
        Grabs the specs for the input tensor \
            of the network. Useful to prepare memory allocations.
       
        Parameters
        ----------
            None

        Returns
        -------
            shape: tuple
                The shape of the input tensor.

            datatype: numpy

        Raises
        ------
            None
        """
        return self.inputs[0]['shape'], self.inputs[0]['dtype']

    def output_spec(self):
        """
        Grabs the specs for the output tensors of the network.
        Useful to prepare memory allocations.

        Parameters
        ----------
            None

        Returns
        -------
            specs: list
                A list with two items per element, the shape and (numpy)
                datatype of each output tensor.

        Raises
        ------
            None
        """
        specs = list()
        for o in self.outputs:
            specs.append((o['shape'], o['dtype']))
        return specs
