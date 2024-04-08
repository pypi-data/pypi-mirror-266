import copy
from quant.utils.io import load_json


cfg = dict(
    data=dict(
        type="FootballDataset",
        data_root="/datasets/table20240326_v0401_2201to2310_label_s5whole",
        train_file="20240402002149.dat",
        test_file="20240402002205.dat",
        batch_size=128),
    model=dict(
        type="STNetV3",
        in_features=98,
        hidden_features=384,
        out_features=10,
        n_layers=1,
        bias=True,
        drop=0.,
        enable_skip=False,
        num_embeddings=2753,
        embedding_dim=100),
    loss=dict(type="CrossEntropyLoss", reduction="mean"),
    optimizer=dict(
        type="SGD",
        lr=0.2,
        momentum=0.9,
        weight_decay=0.0001),
    scheduler=dict(
        type="StepLR",
        step_size=10,
        gamma=0.1),
    runtime=dict(
        seed=1,
        epochs=30,
        device="cuda",
        log_interval=50))


def get_config(config_file=None):
    if config_file:
        _cfg = load_json(config_file)
    else:
        _cfg = copy.deepcopy(cfg)
    return _cfg


def merge_from_str(cfg, args):
    # terminal: model.backbone.depth=50
    # terminal: model.backbone.type='"resnet"'
    # terminal: model.backbone.out_indices='(0, 1, 2, 3)'
    cfg = copy.deepcopy(cfg)
    for arg in args:
        key, val = arg.split("=", maxsplit=1)

        d = cfg
        sub_keys = key.split(".")
        for sub_key in sub_keys[:-1]:
            d.setdefault(sub_key, dict())
            d = d[sub_key]

        sub_key = sub_keys[-1]
        d[sub_key] = eval(val)
    return cfg


def merge_from_dict(cfg, options):
    cfg = copy.deepcopy(cfg)
    for key, val in options.items():
        d = cfg
        sub_keys = key.split(".")
        for sub_key in sub_keys[:-1]:
            d.setdefault(sub_key, dict())
            d = d[sub_key]

        sub_key = sub_keys[-1]
        d[sub_key] = val
    return cfg
