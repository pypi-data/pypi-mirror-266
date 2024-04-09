#  polynomial.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

from __future__ import annotations

from typing import Union

import numpy as np

__all__ = ['Polynomial']


class Polynomial:
    def __init__(self, *coefficients):
        self._coefficients = np.array([])
        self.__unpack_coefficients(*coefficients)
        self._degree = len(self._coefficients) - 1

        self._derivative = None
        self._integral = None

    @property
    def degree(self):
        return self._degree

    @property
    def coefficients(self):
        return self._coefficients

    @property
    def derivative(self) -> Polynomial:
        if self._derivative is None:
            coefficients = np.array([
                (n + 1) * c for n, c in enumerate(self._coefficients[1:])
            ])

            self._derivative = Polynomial(coefficients)

        return self._derivative

    @property
    def integral(self) -> Polynomial:
        if self._integral is None:
            coefficients = np.array([0.0] + [
                1.0 / (n + 1) * c for n, c in enumerate(self._coefficients)
            ])

            self._integral = Polynomial(coefficients)

        return self._integral

    def __str__(self):
        if self._degree >= 0:
            return str(self._coefficients[0]) + " + " + " + ".join([
                f'{k} * x^{n + 1}'
                for n, k in enumerate(self._coefficients[1:])
            ])
        else:
            return ''

    def __getitem__(self, item: int) -> float:
        return self._coefficients[item]

    def __setitem__(self, n: int, coefficient: float):
        if n > self._degree:
            self._coefficients = np.append(self._coefficients,
                                           np.zeros(n - self._degree))
            self._degree = n

        self._coefficients[n] = coefficient
        self._derivative = None
        self._integral = None

    def __call__(self, x: Union[float, np.ndarray]):
        return sum(c * x ** n for n, c in enumerate(self._coefficients))

    def __unpack_coefficients(self, *coefficients):
        for c in coefficients:
            if isinstance(c, (tuple, list, np.ndarray)):
                self._coefficients = np.append(self._coefficients, c)
            else:
                self._coefficients = np.append(self._coefficients, [c])
