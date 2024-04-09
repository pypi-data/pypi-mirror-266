# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------
import pandas as pd
import numpy as np
# FeatureScaling can help us to boostup the  efficiency of data process


class Feature(object):

    def __init__(self):
        pass


class Scaling(object):

    def __init__(self):
        pass

    def Standardization(self, data):  # Standara
        """In this tech, we should use Z-score to replace the real value.
        the Z-score will be calculated as:
            z =(x−μ)/σ
        After Standardization, the feature of results will be altered \
        and follow the Standard Normal Distribution.
        """
        if isinstance(data, np.ndarray):
            data_mean = data.mean()
            data_std = data.std()
        elif isinstance(data, (list, tuple)):
            data = np.array(data)
            data_mean = data.mean()
            data_std = data.std()
        else:
            raise ValueError(
                'Input requires a list or a tuple or a np.array of int/foat num')

        # mean = np.mean(data)
        # std = np.std(data)
        return (data - data_mean) / data_std  # zscored_data

    def MeanNormalization(self, data):  # 均值归一化
        """In this tech, we will normalize the data into the normalized data which own the distribution
        with mean equal to 0, std equal to 1.

        """
        if isinstance(data, np.ndarray):
            data_min = data.min()
            data_max = data.max()
            data_mean = data.mean()
        elif isinstance(data, (list, tuple)):
            data = np.array(data)
            data_min = data.min()
            data_max = data.max()
            data_mean = data.mean()
        else:
            raise ValueError(
                'Input requires a list or a tuple or a np.array of int/foat num')

        MeanNormalized_data = (data - data_mean) / (data_max - data_min)
        return MeanNormalized_data

    def MeanMaxScaling(self, data, scalerange=(0, 1)):
        """
        This Scaling will create the value in [0,1].
        When we are reqired scale the data into special range,
         such as [0,255] in the Image Process Task.
        """
        if isinstance(data, np.ndarray):
            data_min = data.min()
            data_max = data.max()
        elif isinstance(data, (list, tuple)):
            data = np.array(data)
            data_min = data.min()
            data_max = data.max()
        else:
            raise ValueError(
                'Input requires a list or a tuple or a np.array of int/foat num')

        MeanMaxScaled_data = ((data - data_min) / (data_max - data_min)) * \
            (scalerange[1] - scalerange[0]) + scalerange[0]
        return MeanMaxScaled_data


if __name__ == '__main__':
    pass
