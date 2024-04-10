import re
from quant.football.data.utils import convert_odds_data


def filter_odds_data_by_time_range(odds_data, time_range):
    # odds_data = [['77', '1-2', '1.60', '3.5', '0.47', '10-02 00:39', '滚']]
    if len(odds_data) < 1 or len(odds_data[0]) != 7:
        return []

    time_mini, time_maxi = time_range

    pattern = re.compile(r"[0-9]+")

    tmp_time, tmp_odds, tmp_mini = [], [], []
    for row in odds_data:
        time_this = row[0]
        if isinstance(time_this, str) and pattern.fullmatch(time_this):
            time_this = int(time_this)
            if time_this <= time_maxi:
                tmp_time.append(time_this)
                tmp_odds.append(row)
                if time_this <= time_mini:
                    tmp_mini.append(time_this)

    time_mini = max(tmp_mini) if tmp_mini else time_mini

    out = []
    for time_this, row in zip(tmp_time, tmp_odds):
        if time_this >= time_mini:
            out.append(row)

    out = convert_odds_data(out)

    return out


def compute_bet_overunder(probs, odds, conf_thr=0.7):
    # odds = ['77', '1-2', '1.60', '3.5', '0.47', '10-02 00:39', '滚']
    bet_p = float(odds[3])
    bet_c_over = float(odds[2])
    bet_c_under = float(odds[4])

    _id_eq = round(bet_p)
    if bet_p - _id_eq > 0.01:
        _id_gt, _id_lt = _id_eq + 1, _id_eq + 1
    elif bet_p - _id_eq > -0.01:
        _id_gt, _id_lt = _id_eq + 1, _id_eq
    else:
        _id_gt, _id_lt = _id_eq, _id_eq

    _conf_gt, _conf_lt = sum(probs[_id_gt:]), sum(probs[:_id_lt])
    _conf_eq = 1.0 - _conf_gt - _conf_lt

    bet_e, bet_ret = "none", 0.0
    if _conf_gt > _conf_lt:
        if _conf_gt + _conf_eq >= conf_thr:
            bet_e = "over"
            bet_ret = 1.0 + bet_c_over
    else:
        if _conf_lt + _conf_eq >= conf_thr:
            bet_e = "under"
            bet_ret = 1.0 + bet_c_under

    return bet_p, bet_e, bet_ret, _conf_gt, _conf_eq, _conf_lt
