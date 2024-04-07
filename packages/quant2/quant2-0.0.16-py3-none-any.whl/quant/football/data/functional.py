import copy
from quant.utils.io import make_dir, save_json


def filter_values(data, idx, vals, only_matches=True):
    data = copy.deepcopy(data)
    vals = set(vals)

    _data = []
    for row in data:
        if only_matches:
            if row[idx] in vals:
                _data.append(row)
        else:
            if row[idx] not in vals:
                _data.append(row)
    return _data


def count_values(data, idx, display=False):
    counts = {}
    for row in data:
        key = row[idx]
        if key in counts:
            counts[key] += 1
        else:
            counts[key] = 1

    counts = [(k, v) for k, v in counts.items()]
    counts = sorted(counts, key=lambda x: x[1], reverse=True)

    if display:
        print(f"COUNT VALUES:({len(counts)})\n{counts=}")

    return counts


def split_dataset(data, idx):
    data = copy.deepcopy(data)

    _data = {}
    for row in data:
        key = row[idx]
        if key in _data:
            _data[key].append(row)
        else:
            _data[key] = [row]
    return _data


def save_dataset(data, stem, path, exist_ok=True):
    path = make_dir(path, exist_ok)
    file = (path / f"{stem}.json").as_posix()
    save_json(file, data, indent=4)
    return file
