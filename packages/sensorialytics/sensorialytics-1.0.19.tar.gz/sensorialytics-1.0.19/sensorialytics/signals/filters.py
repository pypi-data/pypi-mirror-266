#  filters.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

import numpy as np
from scipy.signal import butter, lfilter

from sensorialytics.mathematics.functions import Symmetrised, Sigmoid
from sensorialytics.mathematics.tools import derive

__all__ = ['Filter', 'ButterworthFilter', 'DerivativeFilter',
           'ComplementaryFilter', 'RecursiveAverageFilter']


class Filter:
    def __init__(self, sampling_frequency: float = 1.0):
        self._sampling_frequency = sampling_frequency
        self._order = 1
        self._initialized = False

    def filter(self, x: np.ndarray, *args) -> np.ndarray:
        """
        :param x: input signals
        :return: filtered signals
        """

        return x.copy()

    def set_sampling_frequency(self, sampling_frequency: float):
        self._sampling_frequency = sampling_frequency


class ButterworthFilter(Filter):
    def __init__(self, order: int, fn: float, filter_type: str,
                 fs: float = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._order = order
        self._fn = fn
        self._filter_type = filter_type

        self.set_sampling_frequency(sampling_frequency=fs)
        self._make_filter()

    def _make_filter(self):
        if self._sampling_frequency is not None:
            self.__b, self.__a = butter(N=self._order, Wn=self._fn,
                                        btype=self._filter_type,
                                        fs=self._sampling_frequency)
            self._initialized = True

    def set_sampling_frequency(self, sampling_frequency: float):
        super().set_sampling_frequency(sampling_frequency)

        self._make_filter()

    def filter(self, x: np.ndarray, *args) -> np.ndarray:
        """
        :param x: input signals
        :return: filtered signals
        """

        if self._initialized:
            return lfilter(self.__b, self.__a, x)
        else:
            raise RuntimeError('Filter not initialized')


class ComplementaryFilter(Filter):
    def __init__(self, gain: float, *args, **kwargs):
        """
        :param gain : gain of the filter
        """
        super().__init__(*args, **kwargs)

        if not (0 < gain < 1):
            raise ValueError('Must be 0 < gain < 1')

        self._gain = gain
        self._complementary_gain = 1.0 - gain

    def filter(self, x: np.ndarray, *args) -> np.ndarray:
        filtered = []
        value = x[0]
        dx = np.array(args[0])

        for xx, dxx in zip(x, dx):
            value = self._gain * xx + self._complementary_gain * (value + dxx)
            filtered.append(value)

        return np.array(filtered)


class DCBlocker(Filter):
    def __init__(self, memory_gain: float, momentum_gain: float, *args,
                 **kwargs):
        """
        :param memory_gain : memory gain
        :param momentum_gain: momentum gain
        """
        super().__init__(*args, **kwargs)

        self._memory_gain = memory_gain
        self._momentum_gain = momentum_gain
        self._complementary_momentum_gain = (1 - self._momentum_gain)

    def filter(self, x: np.ndarray, *args) -> np.ndarray:
        """
        :param x: input signals
        :return: filtered signals
        """

        filtered = [0]
        y = 0
        dxx_old = 0
        dx = (x[1:] - x[:-1])

        for dxx in dx:
            y = self._memory_gain * y + \
                self._momentum_gain * dxx_old + \
                self._complementary_momentum_gain * dxx

            dxx_old = dxx
            filtered.append(y)

        return np.array(filtered)


class DerivativeFilter(Filter):
    def __init__(self, sigma: float = 1.0, cutoff_derivative: float = 0.0,
                 alpha: float = 1.0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._dt = 1.0 / self._sampling_frequency
        self._weight_function = Symmetrised(
            function=Sigmoid(sigma=sigma, x0=cutoff_derivative)
        )

        if (0.0 <= alpha) and (alpha <= 1.0):
            self._alpha = alpha
        else:
            raise ValueError('alpha must be so that 0.0 <= alpha <= 1.0')

    def set_sampling_frequency(self, sampling_frequency: float):
        super().set_sampling_frequency(sampling_frequency)
        self._dt = 1.0 / self._sampling_frequency

    def filter(self, x: np.ndarray, *args) -> np.ndarray:
        derivative = derive(x=x, dx=self._dt)
        filtered = np.zeros(len(x))

        filtered[0] = x[0]

        for i, der in enumerate(derivative[1:]):
            weight = self._weight_function(der)
            delta = weight * der * self._dt
            value = filtered[i] + delta
            filtered[i + 1] = x[i] + self._alpha * (value - x[i])

        return filtered


class RecursiveAverageFilter(Filter):
    def __init__(self, sampling_frequency: float, gain: float):
        super().__init__(sampling_frequency=sampling_frequency)

        self._gain = gain
        self._complementary_gain = 1.0 - gain

    def filter(self, x: np.ndarray, *args) -> np.ndarray:
        filtered = np.zeros(len(x))
        y = x[0]

        for i, xx in enumerate(x):
            y = self._complementary_gain * y + self._gain * xx
            filtered[i] = y

        return filtered
