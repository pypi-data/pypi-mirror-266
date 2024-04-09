#  tools.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import numpy as np

from sensorialytics.mathematics.point import Point
from sensorialytics.mathematics.polynomial import Polynomial

__all__ = ['cast_to_float', 'is_iterable', 'derive', 'simpson_derivative',
           'sign', 'unwrap', 'get_line', 'get_parallel_line',
           'get_lines_intersection']


def cast_to_float(x):
    if is_iterable(x) and not isinstance(x, str):
        return np.array([cast_to_float(v) for v in x])
    else:
        try:
            return float(x)
        except ValueError:
            return np.nan


def is_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def derive(x: np.ndarray, dx: float = 1.0, shift: int = 1):
    return np.append([0], x[shift:] - x[:-shift]) / (shift * dx)


def simpson_derivative(x, dt):
    derivative = np.zeros(x.shape)

    derivative[2:-2] = (x[:-4] - 8 * x[1:-3] + 8 * x[3:-1] - x[4:]) / (12 * dt)

    return derivative


def sign(x):
    return int(x > 0)


def unwrap(x: np.ndarray, mod: float):
    """
    Inverse of np.mod
    :param x: array to unwrap
    :param mod:modulus used to wrap
    :return: unwrapped np.ndarray
    """
    half_mod = mod / 2.0
    unwrapped = np.array([])
    delta = 0.0
    old_x = x[0]

    for v in x:
        if old_x - v > half_mod:
            delta += mod

        unwrapped = np.append(unwrapped, [v + delta])
        old_x = v

    return unwrapped


def get_line(point1: Point, point2: Point) -> Polynomial:
    if point2[0] == point1[0]:
        raise ZeroDivisionError('Can\'t determine the equation if p1_x = p2_x')

    m = (point2[1] - point1[1]) / (point2[0] - point1[0])
    q = point1[1] - m * point1[0]

    return Polynomial(q, m)


def get_parallel_line(line: Polynomial, point: Point) -> Polynomial:
    if line.degree != 1:
        raise RuntimeError('Provided polynomial is not a line')

    m = line[1]
    q = point[1] - m * point[0]

    return Polynomial(q, m)


def get_lines_intersection(line1: Polynomial, line2: Polynomial) -> Point:
    if line1.degree != 1 or line2.degree != 1:
        raise RuntimeError('Polynomials have degree != 1')

    if line1[1] == line2[1]:
        raise RuntimeError('Lines are parallel')

    x = (line2[0] - line1[0]) / (line1[1] - line2[1])
    y = line1[1] * x + line1[0]

    return Point(x, y)
