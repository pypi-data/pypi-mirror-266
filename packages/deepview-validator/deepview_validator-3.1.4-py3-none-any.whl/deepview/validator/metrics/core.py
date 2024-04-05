# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from deepview.validator.exceptions import DivisionByZeroException
import numpy as np

message = ("Unexpected input type of {} is provided. " + 
            "It should be type int. Provided with {} ")

class Metrics:
    """
    Abstract class that provides a template for the metric computations.

    Parameters
    ----------
        None

    Raises
    ------
        DivisionByZeroException
            This will raise the exception if a ZeroDivisionError is caught.

        ValueError
            This will raise the exception if the provided parameters
            in certain methods does not conform to the specified data type
            or the parameters are out of bounds. i.e. The thresholds provided
            are greater than 1 or less than 0.
    """

    @staticmethod
    def validate_threshold(threshold, min=0., max=1.):
        """
        Validates the threshold to be a floating type and \
            does not exceed defined bounds (0...1).
    
        Parameters
        ----------
            threshold: float
                The threshold to validate.

            min: float
                The minimum acceptable threshold.

            max: float
                The maximum acceptable threshold.

        Returns
        -------
            threshold: float
                The validated threshold.

        Raises
        ------
            ValueError
                Raised if the provided threshold is not floating point type.
        """
        if not (isinstance(threshold, (float, np.floating))):
            raise ValueError(
                "The provided threshold is not of numeric type: float. " +
                "Provided with: {}".format(type(threshold)))
        
        if threshold < min:
            return min
        elif threshold > max:
            return max
        else:
            return threshold
       
    @staticmethod
    def divisor(num, denom, info='Basic Division'):
        """
        Performs basic division operations for ratio metrics.

        Parameters
        ----------
            num: int, float, complex
                This is the numerator in the division.

            denom: int, float, complex
                This is the denominator in the division.

            info: str
                This is the description of the operation.
                i.e what is being calculated?

        Returns
        -------
            The division result: int, float, complex
                Resulting value is the result when num/denom is performed.

        Raises
        ------
            DivisionByZeroException
                Raised if the denominator provided is 0.

            ValueError
                Raised if the provided parameters for num and denom
                are not numeric types (int, float, complex).
        """
        if not (isinstance(info, str)):
            raise ValueError(
                "Unexpected input type of info is provided. " +
                "The parameter for info should be of type string. " +
                "Provided with info: {}".format(
                    type(info)))
        
        if not (isinstance(num, (int, float, complex)) or 
                isinstance(num, (np.integer, np.floating, np.complex_))):
            raise ValueError(
                "Unexpected input type of num is provided. " +
                "It should be a numeric datatype of type int, float,  " +
                "or complex. Provided with num: {} ".format(
                    type(num)))
        elif not (isinstance(denom, (int, float, complex)) or 
                  isinstance(denom, (np.integer, np.floating, np.complex_))):
            raise ValueError(
                "Unexpected input type of denom is provided. " +
                "It should be a numeric datatype of type int, float,  " +
                "or complex. Provided with denom: {} ".format(
                    type(denom)))
        else:
            try:
                return num / denom
            except ZeroDivisionError:
                raise DivisionByZeroException(
                    info,
                    num,
                    denom)

    @staticmethod
    def compute_precision(tp, fp):
        """
        Calculates the precision = tp/(tp+fp).

        Parameters
        ----------
            tp: int
                The number of true positives.

            fp: int
                The number of false positives.

        Returns
        -------
            Precision score: float
                Resulting value is the result of tp/(tp+fp).

        Raises
        ------
            DivisionByZeroException
                Raised if tp + fp = 0.

            ValueError
                Raised if the provided parameters for tp and fp
                are not integers or the values for tp and fp
                are negative integers.
        """
        if not isinstance(tp, (int, np.integer)):
            raise ValueError(message.format("tp", type(tp)))
        elif not isinstance(fp, (int, np.integer)):
            raise ValueError(message.format("fp", type(fp)))
        else:
            if (tp < 0 or fp < 0):
                raise ValueError(
                    "tp or fp cannot be less than 0. " +
                    "Provided with tp: {} and fp: {}".format(tp,fp))
            else:
                try:
                    return tp / (tp + fp)
                except ZeroDivisionError:
                    raise DivisionByZeroException(
                        "precision",
                        tp,
                        (tp + fp))

    @staticmethod
    def compute_recall(tp, fn):
        """
        Calculates recall = tp/(tp+fn).

        Parameters
        ----------
            tp: int
                The number of true positives.

            fn: int
                The number of false negatives.

        Returns
        -------
            Recall score: float
                Resulting value is the result of tp/(tp+fn).

        Raises
        ------
            DivisionByZeroException
                Raised if tp + fn = 0.

            ValueError
                Raised if the provided parameters for tp and fn
                are not integers or the values for tp
                and fn are negative integers.
        """
        if not isinstance(tp, (int, np.integer)):
            raise ValueError(message.format("tp", type(tp)))
        elif not isinstance(fn, (int, np.integer)):
            raise ValueError(message.format("fn", type(fn)))
        else:
            if (tp < 0 or fn < 0):
                raise ValueError(
                    "tp or fn cannot be less than 0. " +
                    "Provided with tp: {} and fn: {}".format(tp,fn))
            else:
                try:
                    return tp / (tp + fn)
                except ZeroDivisionError:
                    raise DivisionByZeroException(
                        "recall",
                        tp,
                        (tp + fn))

    @staticmethod
    def compute_accuracy(tp, fp, fn):
        """
        Calculates the accuracy = tp/(tp+fp+fn).

        Parameters
        ----------
            tp: int
                The number of true positives.

            fp: int
                The number of false positives.

            fn: int
                The number of false negatives.

        Returns
        -------
            Accuracy score: float
                Resulting value is the result of tp/(tp+fp+fn).

        Raises
        ------
            DivisionByZeroException
                Raised if tp + fp + fn = 0.

            ValueError
                Raised if the provided parameters for tp, fp, and fn
                are not integers or the values for tp, fp,
                or fn are negative integers.
        """
        if not isinstance(tp, (int, np.integer)):
            raise ValueError(message.format("tp", type(tp)))
        elif not isinstance(fp, (int, np.integer)):
            raise ValueError(message.format("fp", type(fp)))
        elif not isinstance(fn, (int, np.integer)):
            raise ValueError(message.format("fn", type(fn)))
        else:
            if (tp < 0 or fp < 0 or fn < 0):
                raise ValueError(
                    "tp, fn, or fp cannot be less than 0. " +
                    "Provided with tp: {}, fp: {}, fn: {}.".format(
                        tp,
                        fp,
                        fn))
            else:
                try:
                    return tp / (tp + fp + fn)
                except ZeroDivisionError:
                    raise DivisionByZeroException(
                        "accuracy",
                        tp,
                        (tp + fp + fn))
    @staticmethod
    def mean_squared_error(y_true, y_pred):
        """
        Calculates the mean squared error defined in this \
            source: https://www.geeksforgeeks.org/python-mean-squared-error/
        
        Parameters
        ----------
            y_true: list
                The true values.

            y_pred: list
                The predicted values.

        Returns
        -------
            mean squared error: float
                The mean squared error of the values
                comparing y_pred to y_true.

        Raises
        ------
            None
        """
        return np.square(np.subtract(y_true,y_pred)).mean()
    
    @staticmethod
    def mean_absolute_error(y_true, y_pred):
        """
        Calculates the mean absolute error defined in this \
            source: https://datagy.io/mae-python/
    
        Parameters
        ----------
            y_true: list
                The true values.

            y_pred: list
                The predicted values.

        Returns
        -------
            mean absolute error: float
                The mean absolute error of the values
                comparing y_pred to y_true.

        Raises
        ------
            None
        """
        return np.abs(np.subtract(y_true, y_pred)).mean()