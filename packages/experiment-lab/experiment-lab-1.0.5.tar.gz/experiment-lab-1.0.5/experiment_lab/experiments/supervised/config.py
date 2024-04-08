"""Python file containing the configs for the supervised learning experiments."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
from hydra.core.config_store import ConfigStore

from experiment_lab.core.base_config import BaseConfig


class IntervalType(Enum):
    """The log interval type for wandb and logging"""

    batches = 0
    epochs = 1
    batches_and_epochs = 2


@dataclass
class LoggingSchedule:
    log_type: IntervalType = IntervalType.batches
    log_freq: int = 0
    wandb_log_type: IntervalType = IntervalType.batches
    wandb_log_freq: int = 0


@dataclass
class SupervisedConfig(BaseConfig):
    """The Supervised dataclass."""

    dataset: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "torch.utils.data.ConcatDataset",
            "datasets": [
                {
                    "_target_": "torchvision.datasets.MNIST",
                    "root": "./data/supervised/mnist",
                    "download": True,
                    "train": True,
                    "transform": {"_target_": "torchvision.transforms.ToTensor"},
                },
                {
                    "_target_": "torchvision.datasets.MNIST",
                    "root": "./data/supervised/mnist",
                    "download": True,
                    "train": False,
                    "transform": {"_target_": "torchvision.transforms.ToTensor"},
                },
            ],
        }
    )

    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1

    data_loader_kwargs: Dict[str, Any] | None = None

    model: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "torch.nn.Sequential",
            "_args_": [
                {
                    "_target_": "torch.nn.Flatten",
                },
                {
                    "_target_": "experiment_lab.common.networks.create_mlp_network",
                    "layer_sizes": [784, 500, 100, 10],
                },
            ],
        }
    )
    load_model_path: str | None = None

    optimizer: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "torch.optim.Adam",
        }
    )

    scheduler: Dict[str, Any] | None = None

    loss: Dict[str, Any] = field(
        default_factory=lambda: {"_target_": "torch.nn.NLLLoss"}
    )

    num_epochs: int = 10

    save_model_freq: int = 1  # Always by num epochs
    logging_schedule: LoggingSchedule = field(default_factory=LoggingSchedule)

    device: str = "mps"
    gpu_idx: int | None = None

    def __post_init__(self) -> None:
        """Does additional checks on the loaded config."""
        super().__post_init__()
        assert self.num_epochs >= 0, "The number of epochs cannot be less than 0"
        assert self.train_ratio > 0, "The train ratio must be greater than 0"
        assert self.val_ratio > 0, "The val ratio must be greater than 0"
        assert self.test_ratio > 0, "The test ratio must be greater than 0"
        assert (
            self.train_ratio + self.val_ratio + self.test_ratio == 1.0
        ), "All of the data must be split up into train, val, and test such that train_ratio + val_ratio + test_ratio == 1.0"


def register_configs():
    """Registers the supervised config."""
    cs = ConfigStore.instance()
    cs.store(name="supervised_config", node=SupervisedConfig)
