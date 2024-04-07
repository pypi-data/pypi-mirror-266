# 1) PYTHONPATH=$(pwd) python tools/experimental/train_table20240326_v2.py
# 2) python tools/experimental/train_table20240326_v2.py
import numpy as np
import random
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from quant.football.data.dataset import ClassificationDataset
from quant.layers.normalization import RMSNorm
from quant.layers.swiglu_ffn import SwiGLUFFN
from torch.optim.lr_scheduler import StepLR


def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.normal_(m.weight, 0, 0.02)
        if hasattr(m, "bias") and m.bias is not None:
            nn.init.constant_(m.bias, 0.0)


class Net(nn.Module):

    def __init__(self, in_features, hidden_features, out_features, n_layers=1, bias=True):
        super(Net, self).__init__()
        self.emb = nn.Linear(in_features, hidden_features, bias=bias)
        self.layers = nn.ModuleList()
        for _ in range(n_layers):
            self.layers.append(RMSNorm(hidden_features))
            self.layers.append(SwiGLUFFN(hidden_features, bias=bias))
            self.layers.append(nn.SiLU())
        self.out_norm = RMSNorm(hidden_features)
        self.out = nn.Linear(hidden_features, out_features, bias=bias)

    def forward(self, x):
        x = F.silu(self.emb(x))
        for layer in self.layers:
            x = layer(x)
        x = self.out(self.out_norm(x))
        return x


def train(model, device, train_loader, criterion, optimizer, epoch, log_interval=10, dry_run=False):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            print("Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            if dry_run:
                break


def test(model, device, test_loader, criterion):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader)

    print("\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n".format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
    return correct / len(test_loader.dataset)


def main(train_file, test_file, seed=1, device="cuda", batch_size=128, n_layers=1, lr=0.1, epochs=90, log_interval=10):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    if device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    train_dataset = ClassificationDataset(train_file)
    test_dataset = ClassificationDataset(test_file)

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=1
    )

    model = Net(806, 384, 10, n_layers, bias=True).to(device)
    # model.apply(init_weights)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr, 0.9, weight_decay=1e-4)
    scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
    out_dir = Path("runs") / time.strftime("%m%d%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    best_acc = 0.0
    best_epoch = -1
    for epoch in range(1, epochs + 1):
        train(model, device, train_loader, criterion,
              optimizer, epoch, log_interval)
        curr_acc = test(model, device, test_loader, criterion)
        if curr_acc > best_acc:
            best_acc, best_epoch = curr_acc, epoch
        scheduler.step()
        torch.save(model.state_dict(), out_dir / f"model{epoch:03d}.pt")

    print("[best model]")
    print(f"\n{best_acc=:.5f}, {best_epoch=}, path={out_dir}\n")

    print("[check train dataset]")
    check_loader = torch.utils.data.DataLoader(train_dataset, batch_size=1)
    test(model, device, check_loader, criterion)


if __name__ == "__main__":
    data_root = Path("/datasets/table20240326_03281154_torch_norm")
    main(
        train_file=data_root / "20240329_101534.dat",
        test_file=data_root / "20240329_101539.dat",
        seed=1,
        device="cuda",
        batch_size=128,
        n_layers=1,
        lr=0.1,
        epochs=90,
        log_interval=10,
    )
