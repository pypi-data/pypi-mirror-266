import copy
import torch
import torch.nn.functional as F
import traceback
from pathlib import Path
from quant.football.models.stnet import STNetV3
from quant.football.transforms.table20240326 import extract_features, export_dataset
from quant.utils.io import load_json


class FootballInferencer:

    def __init__(self, checkpoint_dir, infer_config="infer.cfg", model_name="best.pt", device="cuda") -> None:
        if device == "cuda" and torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")

        checkpoint_dir = Path(checkpoint_dir)

        model_cfg, preprocess_args, postprocess_kwargs = \
            self._load_configs(checkpoint_dir, infer_config)

        model = self._init_model(model_cfg, checkpoint_dir / model_name)
        model = model.to(device)
        model.eval()

        self.model = model
        self.device = device
        self.preprocess_args = preprocess_args
        self.postprocess_kwargs = postprocess_kwargs
        self.model_name = model_cfg["log"]["out_dir"][5:]

    def _load_configs(self, checkpoint_dir, infer_config):
        cfg_file = checkpoint_dir / infer_config
        assert cfg_file.is_file(), "You must provide a infer configuration file."
        infer_cfg = load_json(cfg_file)

        cfg_file = checkpoint_dir / infer_cfg.get("model", "model.cfg")
        assert cfg_file.is_file(), "You must provide a model configuration file."
        model_cfg = load_json(cfg_file)

        cfg_file = checkpoint_dir / infer_cfg.get("preprocess", "preprocess.cfg")
        assert cfg_file.is_file(), "You must provide a preprocess configuration file."
        preprocess_args = load_json(cfg_file)

        assert "postprocess" in infer_cfg, "You must provide the postprocess parameters."
        postprocess_kwargs = infer_cfg["postprocess"]

        return model_cfg, preprocess_args, postprocess_kwargs

    def _init_model(self, model_cfg, checkpoint):
        model = copy.deepcopy(model_cfg["model"])

        model_type = model.pop("type")
        if model_type == "STNetV3":
            model = STNetV3(**model)
        else:
            raise NotImplementedError(f"Not supported <{model_type}>.")

        model.load_state_dict(torch.load(checkpoint, map_location=torch.device("cpu")))

        return model

    def __call__(self, section):
        error_id, error_msg = 0, section["section_data_id"]

        try:
            x = self.preprocess(section)[0]
        except Exception:
            error_id, error_msg = 1, traceback.format_exc()
            results = section["section_data_id"]

        if error_id != 0:
            return results, error_id, error_msg

        try:
            probs = self.forward(x)
            bets = section["bets"]["bets"]
            results = self.postprocess(probs, bets)
        except Exception:
            error_id, error_msg = 2, traceback.format_exc()
            results = section["section_data_id"]

        # error_id: 0-程序正常, 1-预处理异常, 2-后处理异常
        return results, error_id, error_msg

    def preprocess(self, section):
        device = self.device
        args = self.preprocess_args

        # args: stages, encoder, whole, nc, transforms

        titan = section["mapping_match"]["titan"]
        match_state = titan["match_state"]
        real_start_time = titan["real_start_time"]
        crawler_time = section["event_titan"]["crawler_end_time"]

        # match_state: "1"-上场, "2"-中场, "3"-下场

        time_curr = -1
        if match_state == "1":
            time_curr = (crawler_time - real_start_time) / 60
        if match_state == "3":
            time_curr = 45 + (crawler_time - real_start_time) / 60

        time_mini = 1 + args[0] * 15
        time_maxi = 90 if args[2] else 45
        assert time_mini < time_curr < time_maxi, "This match does not meet the conditions."

        samples = [extract_features(section)]
        X, Y, Z = export_dataset(samples, *args)[:3]
        assert len(X) > 0, "This match contains invalid features."

        x_home = torch.tensor([X[0][0]], dtype=torch.int).to(device)
        x_away = torch.tensor([X[0][1]], dtype=torch.int).to(device)
        x_features = torch.tensor([X[0][2:]], dtype=torch.float).to(device)
        x = (x_home, x_away, x_features)

        return x, Y[0], Z[0]

    def forward(self, x):
        with torch.no_grad():
            output = self.model(x)[0]
            probs = F.softmax(output, dim=-1).tolist()
        return probs

    def postprocess(self, probs, bets):
        # CP: 0-全场, 1-上半场, 2-下半场
        # P: 盘口; E: 方向; C: 赔率
        kwargs = self.postprocess_kwargs

        bet_cps_in = set(kwargs["bet_cps_in"])
        ret_thr = kwargs["ret_thr"]
        ret_conf_thr = kwargs["ret_conf_thr"]

        results = []
        for bet in bets:
            bet_cp = bet["CP"]
            if bet_cp not in bet_cps_in:
                continue

            bet_p = bet["P"]
            bet_e = bet["E"]
            bet_c = bet["C"]

            _id_eq = round(bet_p)
            if bet_p - _id_eq > 0.01:
                _id_gt, _id_lt = _id_eq + 1, _id_eq + 1
            elif bet_p - _id_eq > -0.01:
                _id_gt, _id_lt = _id_eq + 1, _id_eq
            else:
                _id_gt, _id_lt = _id_eq, _id_eq

            _conf_gt, _conf_lt = sum(probs[_id_gt:]), sum(probs[:_id_lt])
            _conf_eq = 1.0 - _conf_gt - _conf_lt

            if bet_e == "over":
                _ret = _conf_eq + _conf_gt * bet_c
                _ret_conf = _conf_eq + _conf_gt
                _bet_times = 1
            elif bet_e == "under":
                _ret = _conf_eq + _conf_lt * bet_c
                _ret_conf = _conf_eq + _conf_lt
                _bet_times = 1
            else:
                continue

            # [赌注, 倍数, 期望收益, 期望概率, 大球概率, 返还概率, 小球概率]
            if _ret > ret_thr and _ret_conf > ret_conf_thr:
                results.append([
                    bet, _bet_times, _ret, _ret_conf, _conf_gt, _conf_eq, _conf_lt
                ])

        return results
