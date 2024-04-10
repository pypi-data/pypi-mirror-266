# PYTHONPATH=$(pwd) python tools/fb_cls_train.py
import numpy as np
import random
import sys
import time
import torch
from copy import deepcopy
from pathlib import Path
from quant.utils.config import get_config, merge_from_dict
from quant.utils.io import copy_file, save_json
from quant.utils.logging import get_logger, print_log


def train(model, device, train_loader, criterion, optimizer, epoch, log_interval, verbose, logger):
    model.train()
    dataloader_size = len(train_loader)
    for batch_idx, (data, target) in enumerate(train_loader, 1):
        data = [e.to(device) for e in data] if isinstance(
            data, (list, tuple)) else data.to(device)
        target = [e.to(device) for e in target] if isinstance(
            target, (list, tuple)) else target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            print_log(
                f"Train Epoch: {epoch} [{batch_idx}/{dataloader_size}] Loss: {loss.item():.6f}", verbose, logger)


def test(model, device, test_loader, criterion, verbose, logger):
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for data, target in test_loader:
            data = [e.to(device) for e in data] if isinstance(
                data, (list, tuple)) else data.to(device)
            target = [e.to(device) for e in target] if isinstance(
                target, (list, tuple)) else target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader)
    dataset_size = len(test_loader.dataset)
    test_acc = correct / dataset_size

    print_log(
        f"\nTest set: Avg loss: {test_loss:.6f}, Acc: {correct}/{dataset_size} ({test_acc:.4f})\n", verbose, logger)
    return test_acc


def main(cfg, verbose=True):
    _cfg = deepcopy(cfg)
    data, model, loss, optimizer, scheduler, runtime = \
        cfg["data"], cfg["model"], cfg["loss"], cfg["optimizer"], cfg["scheduler"], cfg["runtime"]

    seed = runtime.get("seed", 1)
    epochs = runtime.get("epochs", 90)
    device = runtime.get("device", "cuda")
    log_interval = runtime.get("log_interval", 10)

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    if device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    dataset_type = data.pop("type")
    data_root = Path(data["data_root"])
    if dataset_type == "ClassificationDataset":
        from quant.football.data.dataset import ClassificationDataset
        train_dataset = ClassificationDataset(data_root / data["train_file"])
        test_dataset = ClassificationDataset(data_root / data["test_file"])
    elif dataset_type == "FootballDataset":
        from quant.football.data.dataset import FootballDataset
        train_dataset = FootballDataset(data_root / data["train_file"])
        test_dataset = FootballDataset(data_root / data["test_file"])
    else:
        raise NotImplementedError(f"Not supported <{dataset_type}>.")

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=data["batch_size"], shuffle=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=128
    )

    model_type = model.pop("type")
    if model_type == "STNetV1":
        from quant.football.models.stnet import STNetV1
        model = STNetV1(**model).to(device)
    elif model_type == "STNetV2":
        from quant.football.models.stnet import STNetV2
        model = STNetV2(**model).to(device)
    elif model_type == "STNetV3":
        from quant.football.models.stnet import STNetV3
        model = STNetV3(**model).to(device)
    else:
        raise NotImplementedError(f"Not supported <{model_type}>.")

    loss_type = loss.pop("type")
    if loss_type == "CrossEntropyLoss":
        from torch.nn import CrossEntropyLoss
        criterion = CrossEntropyLoss(**loss).to(device)
    else:
        raise NotImplementedError(f"Not supported <{loss_type}>.")

    optimizer_type = optimizer.pop("type")
    if optimizer_type == "SGD":
        from torch.optim import SGD
        optimizer = SGD(model.parameters(), **optimizer)
    elif optimizer_type == "AdamW":
        from torch.optim import AdamW
        optimizer = AdamW(model.parameters(), **optimizer)
    else:
        raise NotImplementedError(f"Not supported <{optimizer_type}>.")

    scheduler_type = scheduler.pop("type")
    if scheduler_type == "StepLR":
        from torch.optim.lr_scheduler import StepLR
        scheduler = StepLR(optimizer, **scheduler)
    else:
        raise NotImplementedError(f"Not supported <{scheduler_type}>.")

    out_dir = Path("runs") / data_root.name / time.strftime("%m%d%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    copy_file(data_root, out_dir, "*.cfg")

    logger = get_logger(__name__, False, out_dir / "log.txt")

    best_acc, best_epoch = 0.0, -1
    for epoch in range(1, epochs + 1):
        train(model, device, train_loader, criterion, optimizer,
              epoch, log_interval, verbose, logger)
        curr_acc = test(model, device, test_loader, criterion,
                        verbose, logger)
        if curr_acc > best_acc:
            best_acc, best_epoch = curr_acc, epoch
            torch.save(model.state_dict(), out_dir / "best.pt")
        scheduler.step()
    torch.save(model.state_dict(), out_dir / "last.pt")

    print_log("[best model]", verbose, logger)
    print_log(f"\noutput dir: {out_dir}", verbose, logger)
    print_log(f"{best_acc=:.4f}, {best_epoch=:03d}\n", verbose, logger)

    print_log("[check train dataset]", verbose, logger)
    check_loader = torch.utils.data.DataLoader(train_dataset, batch_size=128)
    acc_train = test(model, device, check_loader, criterion,
                     verbose, logger)

    _cfg["log"] = {
        "out_dir": str(out_dir),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "best_acc": best_acc,
        "best_epoch": best_epoch,
        "acc_train": acc_train,
    }
    save_json(out_dir / "model.cfg", _cfg, indent=4)

    return best_acc, _cfg


if __name__ == "__main__":
    options = {}
    for arg in sys.argv[1:]:
        key, val = arg.split("=", maxsplit=1)
        options[key] = eval(val)

    cfg = get_config(options.get("config", None))
    cfg = merge_from_dict(cfg, options)

    main(cfg)
