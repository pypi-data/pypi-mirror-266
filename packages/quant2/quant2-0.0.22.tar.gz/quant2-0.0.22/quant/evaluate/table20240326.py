from quant.evaluate.utils import filter_odds_data_by_time_range, compute_bet_overunder
from quant.utils.io import load_json


def betting_experiment(results, sections, whole=True, time_range=(76, 80), conf_thr=0.7):
    if isinstance(results, str):
        results = load_json(results)

    if isinstance(sections, str):
        sections = load_json(sections)

    if isinstance(sections, list):
        sections = {s["mapping_match"]["titan"]["match_id"]: s for s in sections}

    total_bet = 0
    correct_bet = 0
    correct_bet_ret = 0
    for row in results:
        # row = [y, z, y_, probs]
        # z = [比赛ID,比赛时间,比赛状态,联赛名]
        match_id, probs = row[1][0], row[3]

        section = sections[match_id]

        titan = section["mapping_match"]["titan"]
        if whole:
            score = int(titan["home_score"]) + int(titan["visiting_score"])
        else:
            score = int(titan["home_half_score"]) + int(titan["visiting_half_score"])

        bet_odds = []
        for _, odds_data in section["bets_titan"]["odds_overunder"].items():
            bet_odds.extend(filter_odds_data_by_time_range(odds_data, time_range))

        if len(bet_odds) < 1:
            continue

        bet_p, bet_e, bet_ret = compute_bet_overunder(probs, bet_odds[-1], conf_thr)[:3]

        if bet_e != "none":
            if score > bet_p:
                total_bet += 1
                if bet_e == "over":
                    correct_bet += 1
                    correct_bet_ret += bet_ret
            elif score < bet_p:
                total_bet += 1
                if bet_e == "under":
                    correct_bet += 1
                    correct_bet_ret += bet_ret

    n_samples = len(results)
    bet_ratio = total_bet / n_samples
    correct_ratio = correct_bet / total_bet

    print(f"下注: {total_bet}/{n_samples} ({bet_ratio*100:.2f}%)")
    print(f"正确: {correct_bet}/{total_bet} ({correct_ratio*100:.2f}%)")
    print(f"盈亏: {correct_bet_ret/total_bet:.2f} = {correct_bet_ret:.2f}/{total_bet:.2f}")
