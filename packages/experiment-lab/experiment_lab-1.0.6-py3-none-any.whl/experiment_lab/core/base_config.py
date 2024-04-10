"""The file to hold the base configuration object."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List
from hydra.core.config_store import ConfigStore


class NRunMethodEnum(Enum):
    """Method to run multi runs (series or parallel)"""

    series = 0
    parallel = 1


@dataclass
class AnalysisConfig:
    """Config for analysis of this experiment."""

    filters: List[Dict] = field(default_factory=lambda: [])
    wandb_keys: List[str] = field(default_factory=lambda: [])
    index: str | None = None


@dataclass
class BaseConfig:
    """Basic configuration for general experiment runs."""

    experiment_name: str | None = None

    seed: int | None = None

    n_runs: int = 1
    n_run_method: NRunMethodEnum = NRunMethodEnum.series

    wandb: Dict[str, Any] | None = None

    run_analysis: bool = False
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    def __post_init__(self) -> None:
        """Validation checks for base config"""
        assert self.n_runs >= 0, "Number of runs must be at least 0."


def register_configs() -> None:
    """Registers the configs created."""
    cs = ConfigStore.instance()
    cs.store(name="base_config", node=BaseConfig)
