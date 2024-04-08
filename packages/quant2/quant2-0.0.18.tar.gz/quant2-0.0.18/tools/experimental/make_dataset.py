# %%
import quant
from pathlib import Path
from quant.utils.io import load_json, make_dir, save_json
from quant.football.data.utils import filter_samples, train_test
from quant.football.transforms.table20240326 import check_samples, export_dataset
print(f"{quant.__version__=}")

# %%
file = "/datasets/table20240326_v0401/table20240326_plus.json"

# 加载数据
data = load_json(file)
print(f"[1] {len(data)=}, {len(data[0])=}")

# 检测得分数据是否对齐
good_row, bad_row, bad_msg = check_samples(data)
print(f"[2] {len(good_row)=}, {len(bad_row)=}, {len(bad_msg)=}")

# 拆分训练与测试数据子集
train_data, test_data = train_test(good_row, date_sep="2023-10-01", date_min="2022-01-01", date_max="2023-11-01")
print(f"[3] {len(train_data)=}, {len(test_data)=}")

# 忽略比赛不足`n`场的球队比赛
train_data = filter_samples(train_data, team_idxs=[8, 9], limit=3)
print(f"[4] {len(train_data)=}")

# 准备数据目录
out_dir = Path(file).parent.as_posix() + "_2201to2310_s5_label_whole_c15_maxabs"
out_dir = make_dir(out_dir, exist_ok=False)

# 导出数据集
stages, encoder, whole, nc, transforms = 5, "label", True, 15, "maxabs"
X, Y, Z, stages, encoder, whole, nc, transforms = export_dataset(train_data, stages, encoder, whole, nc, transforms)
print(f"[Train] save {len(X)} rows, {len(X[0])} cols, team {encoder['__len__']}")
save_json(out_dir / "train.dat", [X, Y, Z], indent=4)
save_json(out_dir / "preprocess.cfg", [stages, encoder, whole, nc, transforms], indent=4)
X, Y, Z, stages, encoder, whole, nc, transforms = export_dataset(test_data, stages, encoder, whole, nc, transforms)
print(f"[Test] save {len(X)} rows, {len(X[0])} cols, team {encoder['__len__']}")
save_json(out_dir / "test.dat", [X, Y, Z], indent=4)

# 打印输出位置
print(f"\nout_dir:\n{out_dir}")
