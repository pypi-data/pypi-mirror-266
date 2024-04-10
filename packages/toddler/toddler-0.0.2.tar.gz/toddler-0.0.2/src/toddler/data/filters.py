import numpy as np


def robust_median(mat, axis=None) -> np.ndarray:
    m = 3.0

    d = mat - np.median(mat, axis=axis, keepdims=True)
    mdev = np.median(np.abs(d), axis=axis, keepdims=True)
    s = np.abs(d) / mdev

    newmat = np.copy(mat)
    newmat[s > m] = np.nan

    frame = np.nanmedian(newmat, axis=axis)

    return frame
