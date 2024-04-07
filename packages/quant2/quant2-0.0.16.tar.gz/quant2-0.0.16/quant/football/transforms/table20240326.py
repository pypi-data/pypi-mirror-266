import copy
import time
import numpy as np
from typing import Dict, List, Union
from quant.football.data.preprocessing import get_scale_params, scale
from quant.football.data.stats import mean_std, normlize
from quant.football.data.utils import label_encoder, odds_avg_max_min, one_hot_encoder
from quant.utils.io import make_dir, save_json


def parse_attrs_data(data: dict):
    data = data["titan"]

    keys = [
        "match_id",
        "match_time",
        "match_state",
        "season_name",
        "home_score",
        "visiting_score",
        "home_half_score",
        "visiting_half_score",
        "home_team_name",
        "visiting_team_name",
    ]

    # 10: 10(n-key) * 1(none) + 0(none)
    xs = [data[k] for k in keys]
    return xs


def parse_event_data(data: dict):
    data = data["events"]

    keys = [
        ("goalIn", 0),  # 进球
        ("changePlayer", 1),  # 换人
        ("yellowCard", 2),  # 黄牌
        ("redCard", 3),  # 红牌
        ("ownGoal", 4),  # 乌龙
        ("penaltyKick", 5),  # 点球
        ("penaltyKickMiss", 6),  # 射失点球
        ("doubleYellowToRed", 7),  # 两黄变红
    ]

    xs_home = np.zeros((6, len(keys)), dtype=int)
    xs_away = np.zeros((6, len(keys)), dtype=int)
    for event in data:
        for key, idx in keys:
            if key in event:
                kind = event["kind"].lower()
                cycle = event["time"][:-1].split("+")[0]
                cycle = min(max(0, (int(cycle) - 1) // 15), 5)
                if kind == "home":
                    xs_home[cycle][idx] += 1
                if kind == "away":
                    xs_away[cycle][idx] += 1
                break

    # 96: 8(n-key) * 6(n-cycle) + 8(n-key) * 6(n-cycle)
    xs = xs_home.reshape(-1).tolist() + xs_away.reshape(-1).tolist()
    return xs


def parse_odds_data(data: dict):
    first_1x2 = [v[-1] for v in data["odds_1x2"].values() if v]
    first_overunder = [v[-1] for v in data["odds_overunder"].values() if v]
    first_1x2 = odds_avg_max_min(first_1x2)
    first_overunder = odds_avg_max_min(first_overunder)
    # 18: 3(avg-max-min) * 3(1x2) + 3(avg-max-min) * 3(overunder)
    xs = first_1x2 + first_overunder
    return xs


def extract_features(data: dict):
    attrs_data = parse_attrs_data(data["mapping_match"])
    event_data = parse_event_data(data["event_titan"])
    odds_data = parse_odds_data(data["bets_titan"])
    # 124: 10(attrs) + 96(event) + 18(odds)
    xs = attrs_data + event_data + odds_data
    return xs


def check_samples(data: list[list]):
    good_row, bad_row, bad_msg = [], [], []
    for row in data:
        a = int(row[4])  # 主队得分
        b = int(row[5])  # 客队得分
        c = sum([row[i] for i in range(10, 58, 8)])  # 进球
        c += sum([row[i] for i in range(14, 58, 8)])  # 乌龙
        c += sum([row[i] for i in range(15, 58, 8)])  # 点球
        d = sum([row[i] for i in range(58, 106, 8)])  # 进球
        d += sum([row[i] for i in range(62, 106, 8)])  # 乌龙
        d += sum([row[i] for i in range(63, 106, 8)])  # 点球
        if (a + b) == (c + d):
            good_row.append(row)
            continue
        bad_row.append(row)
        bad_msg.append((a, b, c, d))
    return good_row, bad_row, bad_msg


def export_dataset(data: List[List], stages: int, encoder: Union[str, Dict], whole: bool, nc: int, transforms: Union[str, List]):
    # [0:4] : [比赛ID,比赛时间,比赛状态,联赛名]
    # [4:8] : [主队得分,客队得分,主队半场得分,客队半场得分]
    # [8:10] : [主队名称,客队名称]
    # [10:58] : [进球,换人,黄牌,红牌,乌龙,点球,射失点球,两黄变红]x6
    # [58:106] : [进球,换人,黄牌,红牌,乌龙,点球,射失点球,两黄变红]x6
    # [106:124] : [初赔均值,初赔最大,初赔最小]x[胜平负,进球数]
    assert -1 < stages < 7
    sub_len = 8 * stages

    qkeys = []
    scores = []
    team_home = []
    team_away = []
    features_in = []
    for sample in data:
        qkeys.append(sample[0:4])
        scores.append(sample[4:8])
        team_home.append(sample[8])
        team_away.append(sample[9])
        features_in.append(sample[10:(10 + sub_len)] +
                           sample[58:(58 + sub_len)] +
                           sample[106:124])

    if isinstance(encoder, str):
        # method: label, one_hot
        method = encoder
        if method == "label":
            encoder = label_encoder(team_home + team_away)
        elif method == "one_hot":
            encoder = one_hot_encoder(team_home + team_away)
        else:
            raise NotImplementedError(f"Not supported <{encoder=}>.")
    assert isinstance(encoder, dict), f"{type(encoder)=} is not <dict>."

    X, Y, Z = [], [], []
    for _home, _away, _vals, _outs, _qkey in zip(team_home, team_away, features_in, scores, qkeys):
        if _home not in encoder or _away not in encoder or any([v < 0 for v in _vals]):
            continue
        X.append(encoder[_home] + encoder[_away] + _vals)
        if whole:
            Y.append(min(nc - 1, int(_outs[0]) + int(_outs[1])))
        else:
            Y.append(min(nc - 1, int(_outs[2]) + int(_outs[3])))
        Z.append(_qkey)

    if isinstance(transforms, str):
        # method: standard, minmax, maxabs
        method = transforms
        n_features = len(X[0])

        _XT = [[] for _ in range(n_features)]
        for sample in X:
            for idx, val in enumerate(sample):
                _XT[idx].append(val)

        transforms = [None for _ in range(n_features)]
        for idx in range(encoder["__dim__"] * 2, n_features):
            transforms[idx] = get_scale_params(_XT[idx], method)
    assert isinstance(transforms, list), f"{type(transforms)=} is not <list>."

    _X = []
    for sample in X:
        _sample = []
        for val, args in zip(sample, transforms):
            if args is not None:
                _sample.append(scale(val, *args))
            else:
                _sample.append(val)
        _X.append(_sample)
    X = _X

    return X, Y, Z, stages, encoder, whole, nc, transforms


def export_samples(data: list[list], encoder: Union[str, dict], mean: list, std: list, stages: int, whole: bool, norm: bool, path: str):
    # [0:4] : [比赛ID,比赛时间,比赛状态,联赛名]
    # [4:8] : [主队得分,客队得分,主队半场得分,客队半场得分]
    # [8:10] : [主队名称,客队名称]
    # [10:58] : [进球,换人,黄牌,红牌,乌龙,点球,射失点球,两黄变红]x6
    # [58:106] : [进球,换人,黄牌,红牌,乌龙,点球,射失点球,两黄变红]x6
    # [106:124] : [初赔均值,初赔最大,初赔最小]x[胜平负,进球数]
    assert (-1 < stages < 6) if whole else (-1 < stages < 3)
    _data = copy.deepcopy(data)
    qkeys = []
    scores = []
    team_home = []
    team_away = []
    xfeatures = []
    len_slice = 8 * stages
    for row in _data:
        qkeys.append(row[0:4])
        scores.append(row[4:8])
        team_home.append(row[8])
        team_away.append(row[9])
        xfeatures.append(row[10:(10 + len_slice)] +
                         row[58:(58 + len_slice)] + row[106:124])

    if isinstance(encoder, str):
        if encoder == "label":
            encoder = label_encoder(team_home + team_away)
        elif encoder == "one_hot":
            encoder = one_hot_encoder(team_home + team_away)
        else:
            raise NotImplementedError(f"Not supported <{encoder=}>.")
    assert isinstance(encoder, dict), f"{type(encoder)=} is not <dict>."

    X, Y, Z = [], [], []
    for _home, _away, _vars, _outs, _qkey in zip(team_home, team_away, xfeatures, scores, qkeys):
        if any([v < 0 for v in _vars]):
            continue
        if _home in encoder and _away in encoder:
            X.append(encoder[_home] + encoder[_away] + _vars)
            if whole:
                Y.append(min(9, int(_outs[0]) + int(_outs[1])))
            else:
                Y.append(min(9, int(_outs[2]) + int(_outs[3])))
            Z.append(_qkey)

    if mean is None or std is None:
        start_idx, end_idx = encoder["__dim__"] * 2, len(X[0])
        mean, std = mean_std(X, [start_idx], [end_idx])

    if norm:
        X = normlize(X, mean, std)

    if path is None:
        return X, Y, Z, encoder, mean, std, stages, whole, norm

    path = make_dir(path)
    ts = time.strftime("%Y%m%d%H%M%S")

    # .raw: data
    # .dat: [X, Y, Z]
    # .cfg: [encoder, mean, std, stages, whole, norm]
    parameters = [encoder, mean, std, stages, whole, norm]
    save_json(path / f"{ts}.raw", data, indent=4)
    save_json(path / f"{ts}.dat", [X, Y, Z], indent=4)
    save_json(path / f"{ts}.cfg", parameters, indent=4)
    return X, Y, Z, encoder, mean, std, stages, whole, norm
