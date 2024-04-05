# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.writers.core import Writer

class ConsoleWriter(Writer):
    """
    Used to print the metrics on the terminal.
    
    Parameters
    ----------
        None

    Raises
    ------
        None
    """
    def __init__(self):
        super(ConsoleWriter, self).__init__()

    def __call__(self, message, parameters=None, validation_type='detection'):
        """
        When this is called, it prints the metrics on the console.
        
        Parameters
        ----------
            message: dict.
                This message contains information regarding the metrics.
                See README.md (Method Parameters Format) for more information.

            parameters: dict
                This contains information regarding the model and
                validation parameters.
                See README.md (Method Parameters Format) for more information.
                
            validation_type: str
                This is the type of validation performed.
                Either 'detection' or 'segmentation' or 'pose'.

        Returns
        -------
            header: str
                The validation header message.

            summary: str
                The formatted validation showing the metrics.

            timings: str
                The formatted timings of the model.

        Raises
        ------
            None
        """
        if validation_type.lower() == "detection":
            header, summary, timings = \
                self.format_detection_summary(message, parameters)
        elif validation_type.lower() == "segmentation":
            header, summary, timings = \
                self.format_segmentation_summary(message)
        elif validation_type.lower() == "pose":
            header, summary, timings = self.format_pose_summary(message)
        print(header)
        print(summary)
        if timings is not None:
            print(timings)
        return header, summary, timings