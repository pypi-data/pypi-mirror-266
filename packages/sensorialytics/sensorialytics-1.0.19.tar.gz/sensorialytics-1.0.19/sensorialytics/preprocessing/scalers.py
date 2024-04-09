#  scalers.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import numpy
import pandas

from sensorialytics.helpers.exceptions import FitError

__all__ = ['Scaler', 'MultiDimStandardScaler']


class Scaler:
    def __init__(self, scaler_class, fit_variables):
        self.__scaler_class = scaler_class
        self.__fit_variables = fit_variables
        self.__scalers = {}
        self.__fitted = False

    def reset(self):
        self.__scalers = {}
        self.__fitted = False

    def fit(self, df: pandas.DataFrame):
        self.reset()

        for variable in self.__fit_variables:
            scaler = self.__scaler_class()
            scaler.fit(df[[variable]])
            self.__scalers.update({variable: scaler})

        self.__fitted = True

    def transform(self, data, transform_variables: list = None,
                  array_indices: list = None):
        if transform_variables is None:
            transform_variables = self.__fit_variables
        if self.__fitted:
            if isinstance(data, dict):
                transformed = self.__transform_dict(data, transform_variables)

            elif isinstance(data, pandas.DataFrame):
                transformed = self.__transform_data_frame(data,
                                                          transform_variables)

            elif isinstance(data, pandas.Series):
                transformed = self.__transform_series(data, transform_variables)

            elif isinstance(data, numpy.ndarray):
                transformed = self.__transform_array(array_indices, data,
                                                     transform_variables)
            else:
                raise TypeError(f'Type {type(data)} is invalid for scaling '
                                f'transformation')

        else:
            raise FitError('Scaler not fitted')

        return transformed

    def __transform_array(self, array_indices, data, transform_variables):
        if len(data.shape) != 2:
            raise ValueError(f'2D array expected. '
                             f'Got {data.shape}D array instead')

        if len(array_indices) == len(transform_variables):
            transformed = numpy.array([]).reshape(data.shape[0], 0)
            for i, index in enumerate(range(data.shape[1])):
                if index in array_indices:
                    variable = transform_variables[i]
                    scaler = self.__scalers[variable]
                    transformed = numpy.concatenate(
                        arrays=[
                            transformed,
                            scaler.transform(data[:, [index]])
                        ],
                        axis=1
                    )
                else:
                    transformed = numpy.concatenate(
                        arrays=[transformed, data[:, [i]]],
                        axis=1)
        else:
            raise ValueError(
                'Wrong number of array_indices! Expected {}, got {}'.format(
                    len(transform_variables), len(array_indices)))

        return transformed

    def __transform_series(self, data, transform_variables):
        original_variables = list(data.index)
        other_variables = list(data.index.difference(transform_variables))
        transformed = pandas.Series(name=data.name)
        for variable in transform_variables:
            transformed = transformed.append(pandas.Series(
                self.__scalers[variable].transform([[data[variable]]])[0],
                index=[variable]))
        transformed = data[other_variables].append(transformed)[
            original_variables]

        return transformed

    def __transform_data_frame(self, data, transform_variables):
        original_variables = list(data.columns)
        other_variables = list(data.columns.difference(transform_variables))
        transformed = []
        for variable in transform_variables:
            scld = self.__scalers[variable].transform(data[[variable]])
            transformed.append(
                pandas.DataFrame(
                    data=scld,
                    index=data.index,
                    columns=[variable]
                )
            )
        transformed.append(data[other_variables])
        transformed = pandas.concat(transformed, axis=1)[original_variables]

        return transformed

    def __transform_dict(self, data, transform_variables):
        transformed = data.copy()
        for variable in transform_variables:
            scld = self.__scalers[variable].transform([[data[variable]]])[0, 0]
            transformed.update({
                variable: scld
            })

        return transformed

    def fit_transform(self, df: pandas.DataFrame):
        self.fit(df)

        return self.transform(df)


class MultiDimStandardScaler:
    def __init__(self):
        self._mean = None
        self._var = None
        self._std = None
        self.__fitted = None

    def fit(self, df):
        if isinstance(df, pandas.DataFrame):
            data = df.values
        else:
            data = df.copy()

        self._mean = numpy.mean(data, axis=0)
        self._var = numpy.var(data, axis=0)
        self._std = numpy.sqrt(self._var)
        self.__fitted = True

    def transform(self, df):
        if self.__fitted:
            sample_len = len(df)
            scaled = df - numpy.array([self._mean for _ in range(sample_len)])
            scaled = scaled / numpy.array(
                [self._std for _ in range(sample_len)])
        else:
            raise FitError('Scaler not fitted.')

        return scaled

    def fit_transform(self, df):
        self.fit(df)

        return self.transform(df)
