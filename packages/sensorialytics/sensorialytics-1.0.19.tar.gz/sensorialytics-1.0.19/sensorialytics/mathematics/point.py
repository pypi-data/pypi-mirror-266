#  point.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved
import numpy as np

from sensorialytics.helpers.tools import numeric_types

__all__ = ['Point']


class Point:
    def __init__(self, *coordinates):
        self._dimension = 0
        self._coordinates = np.array([])
        self.__unpack_coordinates(*coordinates)

    def __getitem__(self, item: int) -> float:
        return self._coordinates[item]

    def __str__(self):
        to_str = ''

        if len(self._coordinates) != 0:
            to_str = ', '.join([str(np.round(x, 5)) for x in self._coordinates])

        return f'({to_str})'

    def __mul__(self, other):
        if isinstance(other, Point):
            if other.dimension != self._dimension:
                raise ValueError(f'Points have different dimension! '
                                 f'{self._dimension} != {other.dimension}')
            return Point([
                self._coordinates[i] * other._coordinates[i]
                for i in range(self._dimension)
            ])
        elif isinstance(other, numeric_types):
            return Point([
                self._coordinates[i] * other
                for i in range(self._dimension)
            ])

    def __rmul__(self, other):
        return self.__mul__(other)

    @property
    def dimension(self):
        return self._dimension

    @property
    def coordinates(self) -> np.ndarray:
        return self._coordinates

    def __unpack_coordinates(self, *coordinates):
        for c in coordinates:
            if isinstance(c, (tuple, list, np.ndarray)):
                self._coordinates = np.append(self._coordinates, c)
                self._dimension += len(c)
            else:
                self._coordinates = np.append(self._coordinates, [c])
                self._dimension += 1
