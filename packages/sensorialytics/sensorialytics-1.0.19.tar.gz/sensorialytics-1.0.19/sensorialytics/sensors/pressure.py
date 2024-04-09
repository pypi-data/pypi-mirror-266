#  pressure.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

from typing import Union

import numpy as np
import pandas as pd

from .sensor import Sensor

__all__ = ['RemapInput', 'Pressure', 'FSR', 'MatTextile']

RemapInput = Union[np.ndarray, float, int, pd.Series]
RemapOutput = Union[np.ndarray, float, int, pd.Series]


class Pressure(Sensor):
    def __init__(self, remap_parameters: dict = None) -> None:
        super().__init__()

        self._offset = 0.0

        if remap_parameters is not None:
            self._remap_parameters = remap_parameters
        else:
            self._remap_parameters = {}

    def set_remap_parameters(self, remap_parameters: dict):
        self._remap_parameters = remap_parameters

        for name, value in self._remap_parameters.items():
            self.__setattr__(name, value)

    def remap(self, x: RemapInput) -> RemapOutput:
        return x

    def offset(self, o: float):
        self._offset = o

    def get(self, k: str) -> object:
        return self._remap_parameters.get(k)


class FSR(Pressure):
    def __init__(self, remap_parameters: dict = None, use_3_6_v: bool = False):
        super().__init__(remap_parameters=remap_parameters)
        self.__use_3_6_v = use_3_6_v
        self.__scale = (2.4 / 3.6) / 4.0

    def remap(self, x: RemapInput) -> RemapOutput:
        a = self._remap_parameters.get('A')
        b = self._remap_parameters.get('B')
        c = self._remap_parameters.get('C')

        if self.__use_3_6_v:
            x = self.__scale * x

        return a * (np.exp(b * (x - c)) - 1.0) - self._offset


class MatTextile(Pressure):
    def __init__(self, remap_parameters: dict = None):
        super().__init__(remap_parameters=remap_parameters)

    def remap(self, x: RemapInput) -> RemapOutput:
        a = self._remap_parameters.get('A')
        b = self._remap_parameters.get('B')
        c = self._remap_parameters.get('C')

        return a * np.power(x, -b) - c - self._offset
