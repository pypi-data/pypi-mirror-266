import copy
import numpy as np
from typing import Union


def mean_std(data: Union[list[list], np.ndarray], start_idxs: list, end_idxs: list):
    assert (
        isinstance(start_idxs, list)
        and isinstance(end_idxs, list)
        and len(start_idxs) == len(end_idxs)
    )

    n_features = len(data[0])
    mean, std = ["x"] * n_features, [1] * n_features

    for start_idx, end_idx in zip(start_idxs, end_idxs):
        for idx in range(start_idx, end_idx):
            if isinstance(data, list):
                x = [row[idx] for row in data]
            else:
                x = data[:, idx]

            mean[idx] = np.mean(x).item()
            std[idx] = np.std(x).item()

    std = [1 if v < 1e-5 else v for v in std]

    return mean, std


def normlize(data: Union[list[list], np.ndarray], mean: list, std: list):
    if isinstance(data, list):
        _data = []
        for row in data:
            _row = []
            for x, x_mean, x_std in zip(row, mean, std):
                if isinstance(x_mean, (int, float)):
                    _row.append((x - x_mean) / x_std)
                else:
                    _row.append(x)
            _data.append(_row)
    else:
        _data = copy.deepcopy(data)
        for idx, (x_mean, x_std) in enumerate(zip(mean, std)):
            if isinstance(x_mean, (int, float)):
                _data[:, idx] = (data[:, idx] - x_mean) / x_std
            else:
                _data[:, idx] = data[:, idx]
    return _data


def test():
    X = [(np.random.normal(size=100000) * i + i).tolist()
         for i in [1, 2, 4, 6, 8]]
    X = np.asarray(X).transpose((1, 0))

    X1 = X.tolist()
    X2 = X.copy()

    def _show_mean_std(*args):
        for v in args:
            print([f"{vi:.2f}" if isinstance(vi, float) else vi for vi in v])

    mean, std = mean_std(X1, [0], [3])
    _mean, _std = mean_std(normlize(X1, mean, std), [0], [5])
    _show_mean_std(["X1"], mean, std, _mean, _std)

    mean, std = mean_std(X2, [0], [5])
    _mean, _std = mean_std(normlize(X2, mean, std), [0], [5])
    _show_mean_std(["X2"], mean, std, _mean, _std)
