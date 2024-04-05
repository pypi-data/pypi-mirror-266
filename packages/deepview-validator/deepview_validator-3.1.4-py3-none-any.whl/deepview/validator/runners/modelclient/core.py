# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import ModelRunnerFailedConnectionException
from deepview.validator.exceptions import MissingLibraryException
from deepview.validator.runners.core import Runner

class ModelClientRunner(Runner):
    """
    Uses the modelclient API to run DeepViewRT models.

    Parameters
    ----------
        model_path: str
            The path to the model.

        target: str
            The modelrunner target in the EVK. Ex. 10.10.40.205:10817.

    Raises
    ------
        ModelRunnerFailedConnectionException
            Raised if connecting to modelrunner is unsuccessful.

        MissingLibraryException
            Raised if certain libraries are not installed.
    """
    def __init__(
        self,
        model_path,
        target
    ):
        self.model_path = model_path
        self.target = target
        super(ModelClientRunner, self).__init__(model_path)

    def load_model(self):
        """
        Loads the model to the modelrunner target.
      
        Parameters
        ----------
            None

        Returns
        -------
            None

        Raises
        ------
            ModelRunnerFailedConnectionException
                Raised if connecting to modelrunner is unsuccessful.

            MissingLibraryException
                Raised if the library requests is not installed.
        """
        try:
            import requests as req
        except ImportError:
            raise MissingLibraryException(
                "requests is needed to communicate " +
                "with the modelclient server.")

        try:
            from deepview.rt.modelclient import ModelClient
            self.client = ModelClient(
                uri=self.target,
                rtm=self.model_path,
            )
        except req.exceptions.ConnectionError:
            raise ModelRunnerFailedConnectionException(self.target)

        self.device = req.get(self.target).json()["engine"]

        response = req.get("{}/model".format(self.target))
        self.parameters = {}
        if response.status_code == 200:
            body = response.json()
            inputs = body['inputs']
            outputs = body['outputs']
            self.parameters['input_name'] = inputs[0]['name']
            self.parameters['input_type'] = inputs[0]['datatype']
            self.parameters['input_scale'] = inputs[0]['scale']
            self.parameters['input_zp'] = inputs[0]['zero_point']
            self.parameters['input_shape'] = inputs[0]['shape'][1:]
            
            output_parameters = dict()
            for key in outputs:
                output_parameters[key['name']] = {
                    "scale": key['scale'],
                    "zero_point": key['zero_point'],
                    "index": key['index'],
                    "datatype": key['datatype'],
                    "shape": key['shape']
                }
            self.parameters['outputs'] = output_parameters

        else:
            raise ValueError(
                "Bad url was provided and the model is not " +
                "running in specified target !")
    
    @staticmethod
    def apply_normalization(image, norm_type, input_type):
        """
        Performs images normalizations (signed, unsigned, raw).

        Parameters
        ----------
            image: np.ndarray
                The image to perform normalization.

            norm_type: str
                The image normalization type to perform. Ex. 'unsigned'

            input_type: str
                The datatype to cast the final numpy array. Ex. 'uint8'

        Returns
        -------
            image: np.ndarray
                Depending on the normalization, the image will be returned.

        Raises
        ------
            None
        """
        import numpy as np
       
        if norm_type == 'signed':
            return np.expand_dims((image / 127.5) - 1.0, 0) \
                    .astype(np.dtype(input_type))
        elif norm_type == 'unsigned':
            return np.expand_dims(image / 255.0, 0) \
                    .astype(np.dtype(input_type))
        else:
            return np.expand_dims(image, 0) \
                .astype(np.dtype(input_type))