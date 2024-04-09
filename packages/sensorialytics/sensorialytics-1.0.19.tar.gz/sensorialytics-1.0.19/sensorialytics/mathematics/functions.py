#  functions.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

from typing import Union

import numpy as np

__all__ = ['Function', 'Sigmoid', 'SignSigmoid', 'Step', 'Characteristic',
           'Symmetrised']

FunctionInput = Union[np.ndarray, float, int]

EXP_ARG_OVERFLOW = np.log(np.finfo(np.float).max)


class Function:
    def __init__(self):
        pass

    def __call__(self, x: FunctionInput):
        return x


class Sigmoid(Function):
    def __init__(self, sigma: float, x0: float = 0.0):
        super().__init__()
        self._sigma = sigma
        self._x0 = x0

    def __call__(self, x: FunctionInput):
        k = np.minimum(x, EXP_ARG_OVERFLOW)
        e = np.exp(k)

        return e / (1 + e)


class SignSigmoid(Sigmoid):
    def __init__(self, sigma: float, x0: float = 0.0):
        super().__init__(sigma, x0)

    def __call__(self, x: FunctionInput):
        return 2.0 * super()(x) - 1.0


class Step(Function):
    def __init__(self, threshold: float = 0.0):
        super().__init__()

        self._threshold = threshold

    def __call__(self, x: FunctionInput):
        if isinstance(x, np.ndarray):
            return (x >= self._threshold).astype(float)
        else:
            return float(x >= self._threshold)


class Characteristic(Function):
    def __init__(self, lower, upper):
        super().__init__()

        if lower < upper:
            self._lower = Step(lower)
            self._upper = Step(upper)
        else:
            raise ValueError('must be lower < upper')

    def __call__(self, x: FunctionInput):
        return self._lower(x) - self._upper(x)


class Symmetrised(Function):
    def __init__(self, function: Function):
        super().__init__()

        self._base_function = function

    def __call__(self, x: FunctionInput):
        pos = self._base_function(+x) * (x >= 0)
        neg = self._base_function(-x) * (x < 0)

        return pos + neg
