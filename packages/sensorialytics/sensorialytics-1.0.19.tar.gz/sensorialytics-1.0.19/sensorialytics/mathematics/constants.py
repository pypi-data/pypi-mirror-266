#  constants.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

import numpy as np

__all__ = ['PI', 'G', 'GYRO_CONV']

PI: float = np.pi
G: float = 9.80665
GYRO_CONV: float = np.pi / 180.0
