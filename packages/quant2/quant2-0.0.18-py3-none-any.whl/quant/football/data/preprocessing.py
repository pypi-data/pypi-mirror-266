import numpy as np


def scale(x, x_add, x_mul, with_centering, with_scaling):
    if with_centering:
        x += x_add
    if with_scaling:
        x *= x_mul
    return x


def get_scale_params(X, method="standard"):
    x_add, x_mul, with_centering, with_scaling = 0., 1., False, False

    X = np.asarray(X)

    if method == "standard":
        x_mean = X.mean().item()
        x_std = X.std().item()

        with_centering = True
        x_add = 0.0 - x_mean

        if x_std > 1e-6:
            with_scaling = True
            x_mul = 1.0 / x_std
    elif method == "minmax":
        x_min = X.min().item()
        x_range = X.max().item() - x_min

        with_centering = True
        x_add = 0.0 - x_min

        if x_range > 1e-6:
            with_scaling = True
            x_mul = 1.0 / x_range
    elif method == "maxabs":
        x_max_abs = np.abs(X).max()

        if x_max_abs > 1e-6:
            with_scaling = True
            x_mul = 1.0 / x_max_abs

    return x_add, x_mul, with_centering, with_scaling


def maxabs_scale():
    pass


def minmax_scale():
    pass


def standard_scale():
    pass


class MaxAbsScaler:
    pass


class MinMaxScaler:
    pass


class StandardScaler:
    pass


class LabelEncoder:
    pass


class LabelEncoder:
    pass


class OneHotEncoder:
    pass
