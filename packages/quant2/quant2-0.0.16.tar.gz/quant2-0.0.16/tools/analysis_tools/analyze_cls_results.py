from quant.utils.io import load_json


def error_analysis(results, thresholds=[0.3, 0.5, 0.6, 0.7, 0.8]):
    if isinstance(results, str):
        results = load_json(results)

    table = []
    for y, z, y_, probs in results:
        # [比赛ID,比赛时间,比赛状态,联赛名]
        match_id, season_name = z[0], z[3]
        prob, isok = probs[y_], y == y_
        table.append([match_id, season_name, prob, isok])

    logs, gdatas = [], []
    for threshold in thresholds:
        gdata = {}
        for row in table:
            season_name = row[1]
            _n, _n_in, _n_in_ok = gdata.get(season_name, [0, 0, 0])
            is_in = row[2] >= threshold
            is_ok = row[3]
            _n += 1
            if is_in:
                _n_in += 1
                if is_ok:
                    _n_in_ok += 1
            gdata[season_name] = [_n, _n_in, _n_in_ok]

        g_n, g_n_in, g_n_in_ok = 0, 0, 0
        for n, n_in, n_in_ok in gdata.values():
            g_n += n
            g_n_in += n_in
            g_n_in_ok += n_in_ok

        logs.append((
            f"阈值: {threshold:.2f}"
            f", 留存率: {g_n_in/g_n*100:6.2f}% ({g_n_in}/{g_n})"
            f", 准确率: {g_n_in_ok/g_n_in*100:6.2f}% ({g_n_in_ok}/{g_n_in})"))
        gdatas.append({"threshold": threshold, "gdata": gdata})
    return logs, gdatas
