import sys
import torch
import torch.nn.functional as F
from pathlib import Path
from quant.football.models.stnet import STNetV3
from quant.utils.io import load_json, make_dir, save_json


def load_model(model, checkpoint):
    model_type = model.pop("type")
    if model_type == "STNetV3":
        model = STNetV3(**model)
    else:
        raise NotImplementedError(f"Not supported <{model_type}>.")

    model.load_state_dict(torch.load(checkpoint))

    return model


def test_dataset(test_file, checkpoint_dir, output_dir=None, device="cuda"):
    if device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    checkpoint_dir = Path(checkpoint_dir)
    config = load_json(checkpoint_dir / "config.json")

    model = load_model(config["model"], checkpoint_dir / "best.pt")
    model = model.to(device)
    model.eval()

    results, correct = [], 0
    X, Y, Z = load_json(test_file)[:3]
    with torch.no_grad():
        for x, y, z in zip(X, Y, Z):
            x_home = torch.tensor([x[0]], dtype=torch.int).to(device)
            x_away = torch.tensor([x[1]], dtype=torch.int).to(device)
            x_features = torch.tensor([x[2:]], dtype=torch.float).to(device)
            data = (x_home, x_away, x_features)

            output = model(data)[0]
            y_ = output.argmax().item()
            probs = F.softmax(output, dim=-1).tolist()

            results.append([y, z, y_, probs])
            if y == y_:
                correct += 1

    dataset_size = len(results)
    test_acc = correct / dataset_size
    print(f"\nAcc: {correct}/{dataset_size} ({test_acc:.4f})\n")

    if output_dir is not None:
        output_dir = make_dir(output_dir, exist_ok=True)
        save_json(output_dir / Path(test_file).name, results)

    return results, test_acc


if __name__ == "__main__":
    kwargs = {
        "output_dir": None,
        "device": "cuda",
    }
    for arg in sys.argv[1:]:
        key, value = arg.split("=", maxsplit=1)
        kwargs[key] = value

    test_dataset(**kwargs)
