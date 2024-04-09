#  image.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import cv2
import numpy as np

__all__ = ['image_to_signal']


def image_to_signal(path: str, rescale=True):
    img = cv2.imread(path, 0)
    indices = np.array([np.arange(len(img)) + 1 for _ in img[0]]).T

    mask = (img.min(axis=0) < 150)

    signal = indices * (img < 150)
    signal = signal.sum(axis=0)[mask] / (signal > 0).sum(axis=0)[mask]

    if rescale:
        signal = (signal - signal.min()) / (signal.max() - signal.min())

    return signal
