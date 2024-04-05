import skimage.measure
import skimage.morphology
import torch
from torch import Tensor
from PySide6.QtCore import QPointF

import numpy as np
from typing import List


def find_contours(mask):
    return skimage.measure.find_contours(mask.astype(float))[0]

def approximate_polygon(contours, tolerance):
    return skimage.measure.approximate_polygon(contours, tolerance=tolerance)



def mask_to_polygon(mask: np.array, tolerance: float = 1) -> np.array:
    """
    Converts a binary mask to a polygon which can be rendered by the screen.

    Shapes:
        - mask: [x, y]
        - returns: [N, 2]

    :param mask: binary mask
    :return: contors of binary mask as polygon vertices
    """

    contours = skimage.measure.find_contours(mask.astype(float))[0]
    contours = skimage.measure.approximate_polygon(contours, tolerance=tolerance)
    return contours


def polygon_to_qt(contours: np.ndarray) -> List[QPointF]:
    qt_points = []
    for i in range(contours.shape[0]):
        x: float = contours[i, 0]
        y: float = contours[i, 1]
        p = QPointF(x, y)
        qt_points.append(p)

    return qt_points
