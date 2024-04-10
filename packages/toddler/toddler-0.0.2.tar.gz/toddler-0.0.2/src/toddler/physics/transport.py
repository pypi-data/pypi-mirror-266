import numpy as np


def fit_field_with_polynomial(x, field, order=2, axis=0):
    assert len(x) == field.shape[axis]
    assert len(np.shape(field)) <= 2

    if axis != 0:
        field = np.moveaxis(field, axis, 0)

    p = np.polyfit(x, field, order)
    field_fit = get_nth_order_polyval(p, x, n=0, axis=0)

    field_fit = np.moveaxis(field_fit, 0, axis)
    p = np.moveaxis(p, 0, axis)
    return p, field_fit


def polyval_rowwise(p, x):
    if len(np.shape(p)) == 1:
        return np.polyval(p, x)
    else:
        return np.array([np.polyval(p[:, i], x) for i in range(np.shape(p)[1])]).T


def polyder_rowwise(p, n):
    if len(np.shape(p)) == 1:
        return np.polyder(p, n)
    else:
        return np.array([np.polyder(p[:, i], n) for i in range(np.shape(p)[1])]).T


def get_nth_order_polyval(p, x, n=0, axis=0):
    if axis != 0:
        p = np.moveaxis(p, axis, 0)

    if n > 0:
        p_n = polyder_rowwise(p, n)
    else:
        p_n = p
    val = polyval_rowwise(p_n, x)

    val = np.moveaxis(val, 0, axis)
    return val


def get_volume_elements(X, Y):
    dr = np.abs(np.diff([Y[0, :2]])[0][0])
    dz = np.abs(np.diff([X[:2, 0]])[0][0])
    R = np.abs(Y, dtype=np.float32)
    dA = np.pi * ((R + dr / 2) ** 2 - np.maximum(R - dr / 2, 0) ** 2)
    dV = dA * dz

    return dA, dV
