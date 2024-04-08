import copy
import numpy as np
from datetime import datetime
from prettytable import PrettyTable
from typing import Union


def time_secs2str(secs: Union[int, float]):
    return datetime.fromtimestamp(secs).strftime("%Y-%m-%d %H:%M:%S")


def time_str2secs(text: str, year: str = None):
    if " " in text:
        str_date, str_time = text.split(" ")
    else:
        str_date, str_time = text, "00:00:00"

    arr_date = [f"0{s}" if len(s) == 1 else s for s in str_date.split("-")]
    arr_time = [f"0{s}" if len(s) == 1 else s for s in str_time.split(":")]

    if year is not None and len(arr_date) == 2:
        arr_date = [year] + arr_date

    text = "-".join(arr_date) + " " + ":".join(arr_time)
    return datetime.fromisoformat(text).timestamp()


def get_start_time(data: list[dict]):
    first_start_time, second_start_time = 0, 0
    for row in data:
        if row["match_state"] == "1":  # 上半场
            first_start_time = max(first_start_time, row["real_start_time"])
        elif row["match_state"] == "3":  # 下半场
            second_start_time = max(second_start_time, row["real_start_time"])
    return int(first_start_time), int(second_start_time)


def trans_odds_data(data: list[list]):
    def _trans(val):
        if isinstance(val, str):
            if "/" in val:  # 2.5/3
                nums = [float(s) for s in val.split("/")]
                return f"{sum(nums)/len(nums):.2f}"
            return val
        return ""

    data = [["", ""] + v if len(v) == 5 else v for v in data]

    assert all([len(v) == 7 for v in data]), "Odds data must be a list of length 7."
    return [[_trans(vi) for vi in v] for v in data if "封" not in v]


def x_avg_max_min(data: list, weights: list = None):
    if len(data) < 1:
        return [-1.0, -1.0, -1.0]

    if isinstance(data[0], str):
        data = [float(x) for x in data]

    if weights is not None:
        x_avg = sum([x * w for x, w in zip(data, weights)]) / sum(weights)
    else:
        x_avg = sum(data) / len(data)

    x_max = max(data)
    x_min = min(data)

    return [x_avg, x_max, x_min]


def odds_avg_max_min(data: list[list]):
    data = trans_odds_data(data)
    x1 = x_avg_max_min([row[2] for row in data])
    x2 = x_avg_max_min([row[3] for row in data])
    x3 = x_avg_max_min([row[4] for row in data])
    return x1 + x2 + x3


def cycle_difference(seq: list, cycle: int, keeps: list[int]):
    mat = np.asarray(seq).reshape((-1, cycle))

    ref = np.zeros_like(mat)
    ref[1:, :] = mat[:-1, :]

    for idx in keeps:
        ref[:, idx] = 0

    ref[mat < 0] = 0

    return (mat - ref).reshape(-1).tolist()


def filter_samples(data: list[list], team_idxs: list, limit: int = 5):
    data = copy.deepcopy(data)

    counts = {}
    for row in data:
        for idx in team_idxs:
            name = row[idx]
            if name in counts:
                counts[name] += 1
            else:
                counts[name] = 1

    _data = []
    for row in data:
        if any([counts[row[idx]] < limit for idx in team_idxs]):
            continue
        _data.append(row)
    return _data


def train_test(data: list[list], date_sep: str, date_min: str = "2020-01-01", date_max: str = "2099-01-01"):
    _data = copy.deepcopy(data)

    date_sep = time_str2secs(date_sep)
    date_min = time_str2secs(date_min)
    date_max = time_str2secs(date_max)

    train_data, test_data = [], []
    for row in _data:
        ts = row[1]  # match_time
        if ts < date_min:
            continue
        elif ts < date_sep:
            train_data.append(row)
        elif ts < date_max:
            test_data.append(row)

    return train_data, test_data


def one_hot_encoder(names: list[str]):
    names = sorted(set(names))
    eye = np.eye(len(names), k=0, dtype=int)
    encoder = {n: v for n, v in zip(names, eye.tolist())}
    encoder["__len__"] = len(names)
    encoder["__dim__"] = len(names)
    return encoder


def label_encoder(names: list[str]):
    names = sorted(set(names))
    encoder = {n: [i] for i, n in enumerate(names)}
    encoder["__len__"] = len(names)
    encoder["__dim__"] = 1
    return encoder


def count_values(data: list, sort_by: str = "label"):
    counts = {}
    for x in data:
        if x in counts:
            counts[x] += 1
        else:
            counts[x] = 1

    counts = [(k, v) for k, v in counts.items()]

    index = 0 if sort_by == "label" else 1
    counts = sorted(counts, key=lambda x: x[index])

    table_data = PrettyTable()
    table_data.field_names = ["label", "count"]
    table_data.align["label"] = "l"
    table_data.align["count"] = "r"
    table_data.add_rows(counts)
    print(table_data)

    return counts
