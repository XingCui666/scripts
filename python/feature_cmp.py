#!/usr/bin/env python
# coding: utf-8
import numpy as np
import cv2


def cos(vector1, vector2):
    dot_product = 0.0
    norm1 = 0.0
    norm2 = 0.0
    for a, b in zip(vector1, vector2):
        dot_product += a*b
        norm1 += a**2
        norm2 += b**2
    if norm1 == 0.0 or norm2 == 0.0:
        return None
    else:
        return dot_product / ((norm1 * norm2) ** 0.5)


if __name__ == '__main__':
    pc = np.fromfile('feature.bin', dtype=np.float32)
    rk3288 = np.fromfile('feature_3288.bin', dtype=np.float32)
    val = cos(pc, rk3288)

    print(val)
    print('OK')
