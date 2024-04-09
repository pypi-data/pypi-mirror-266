#  detectors.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

from typing import Tuple

import numpy as np
import pandas as pd

__all__ = ['Detector', 'Window', 'SymmetricWindow', 'PeaksValleysDetector']

F = 0.8

DetectorInput = (np.ndarray, pd.Series)


class Detector:
    def __init__(self):
        pass


class PeaksValleysDetector(Detector):
    def __init__(self):
        super().__init__()

        self._window = SymmetricWindow()
        self._start_window_width = 1

        self._sampling_frequency = 0.0

        self._min_height = 0.0

        self._max_reset_time = 2.0
        self._reset_time = 0.0

        self._peaks = np.array([]).reshape((-1, 2))
        self._valleys = np.array([]).reshape((-1, 2))
        self._mv_avg = []
        self._found_peak = False
        self._found_valley = False

    def detect(self, x: DetectorInput, start_sec_in_window: float,
               min_sec_in_window: float, max_sec_in_window: float,
               min_height: float,
               sampling_frequency: float) -> Tuple[np.ndarray, np.ndarray]:
        self.reset()

        self._sampling_frequency = sampling_frequency
        self._start_window_width = int(
            start_sec_in_window * sampling_frequency)
        self._min_height = min_height

        values = self.__get_values(x)

        self._window = SymmetricWindow(
            x=values,
            width=self._start_window_width,
            min_width=int(min_sec_in_window * sampling_frequency),
            max_width=int(max_sec_in_window * sampling_frequency)
        )

        self.__detect(values)

        return np.array(self._peaks), np.array(self._valleys)

    def reset(self):
        self._peaks = np.array([]).reshape((-1, 2))
        self._valleys = np.array([]).reshape((-1, 2))
        self._mv_avg = []
        self._found_peak = False
        self._found_valley = False

    @staticmethod
    def __get_values(x: DetectorInput) -> np.ndarray:
        if isinstance(x, pd.Series):
            return x.values
        else:
            return x

    def __detect(self, x: np.ndarray):
        for i in range(self._window.half_width, len(x)):
            x_range = self._window.get(i)

            self._mv_avg.append([i, x_range.mean()])

            self.__find_peak(i, x_range, x[i])
            self.__find_valley(i, x_range, x[i])
            self.__check_reset()

    def __find_peak(self, i, x_range, value):
        if self._found_valley:
            is_max = x_range.max() == value
            is_high_enough = value - self._mv_avg[-1][1] > self._min_height

            if is_max and is_high_enough:
                self._found_peak = True
                self._peaks = np.append(self._peaks, [[i, value]], axis=0)

                self.__on_found_all()

    def __find_valley(self, i, x_range, value):
        is_min = x_range.min() == value
        is_low_enough = self._mv_avg[-1][1] - value > self._min_height

        if is_min and is_low_enough:
            self._found_valley = True
            self._valleys = np.append(self._valleys, [[i, value]], axis=0)

    def __check_reset(self):
        if self._found_peak or self._found_valley:
            self._reset_time += 1.0 / self._sampling_frequency

            if self._reset_time > self._max_reset_time:
                self._reset_time = 0.0
                self._found_peak = False
                self._found_valley = False

                self._window.set_width(self._start_window_width)

    def __on_found_all(self):
        self._found_valley = False
        self._found_peak = False
        self._reset_time = 0.0

        delta = 2 * (self._valleys[-1, 0] - self._peaks[-1, 0])
        width = 0.8 * 0.5 * delta
        width = int(F * self._window.width + (1 - F) * width)

        self._window.set_width(width)

        self._max_reset_time = 2 * self._window.width / self._sampling_frequency


class Window:
    def __init__(self, x: np.ndarray = np.array([]),
                 width: int = 1, min_width: int = 0, max_width: int = np.inf):
        self._x = x
        self._width = 0
        self._min_width = min_width
        self._max_width = max_width

        self.set_width(width)

    @property
    def width(self):
        return self._width

    @property
    def min_width(self):
        return self._min_width

    @property
    def max_width(self):
        return self._max_width

    def set_width(self, width: int):
        self._width = max(self._min_width, min(width, self._max_width))

    def set_min_width(self, min_width: int):
        self._min_width = min_width

    def set_max_width(self, max_width: int):
        self._max_width = max_width


class SymmetricWindow(Window):
    def __init__(self, x: np.ndarray = np.array([]),
                 width: int = 3, max_width: int = 3, min_width: int = 3):
        self._half_width = 0

        super().__init__(x=x, width=width, min_width=min_width,
                         max_width=max_width)

    @property
    def half_width(self):
        return self._half_width

    def get(self, i: int) -> np.ndarray:
        start = max(0, i - self._half_width)
        end = min(i + self._half_width, len(self._x))

        return self._x[start:end]

    def set_width(self, width: int):
        super().set_width(width)
        self._half_width = self._width // 2
