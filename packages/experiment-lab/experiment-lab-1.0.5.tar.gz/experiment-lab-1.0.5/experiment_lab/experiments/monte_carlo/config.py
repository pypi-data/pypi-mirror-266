"""Python file containing the configs for monte carlo experiments."""

from dataclasses import dataclass, field
from typing import Any, Dict
from hydra.core.config_store import ConfigStore

from experiment_lab.core.base_config import BaseConfig


@dataclass
class MCConfig(BaseConfig):
    """The Monte Carlo dataclass."""

    n_samples: int = 10
    batch_size: int | None = None
    aggregate_every_batch: bool = False
    log_results: bool = False

    sampler: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "experiment_lab.experiments.monte_carlo.UniformSampler"
        }
    )

    aggregator: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "experiment_lab.experiments.monte_carlo.NpAggregator"
        }
    )

    sample_filter: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "experiment_lab.experiments.monte_carlo.PassThroughSampleFilter"
        }
    )

    post_processor: Dict[str, Any] = field(
        default_factory=lambda: {
            "_target_": "experiment_lab.experiments.monte_carlo.PassThroughPostProcessor"
        }
    )

    def __post_init__(self) -> None:
        """Does additional checks on loaded config."""
        super().__post_init__()
        assert self.n_samples >= 0, "Number of samples must be at least 0."
        assert (
            self.batch_size is None or self.batch_size > 0
        ), "Number of samples must be at least 1 or set to None"


def register_configs():
    """Registers the rl config."""
    cs = ConfigStore.instance()
    cs.store(name="mc_config", node=MCConfig)
