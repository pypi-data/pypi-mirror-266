#! /usr/bin/env python3
# vim:fenc=utf-8

from pathlib import Path

import torchvision
from torch.utils.data import DataLoader


def load(path=Path("./res/MNIST"), batch_size=64, shuffle=True):
    normalise_data = torchvision.transforms.Compose(
        [
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0.5,), (0.5,)),
        ]
    )
    train_dataset = torchvision.datasets.MNIST(
        str(path),
        train=True,
        download=True,
        transform=normalise_data,
    )
    test_dataset = torchvision.datasets.MNIST(
        str(path),
        train=False,
        download=True,
        transform=normalise_data,
    )
    trainloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=shuffle)
    testloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=shuffle)
    return trainloader, testloader
