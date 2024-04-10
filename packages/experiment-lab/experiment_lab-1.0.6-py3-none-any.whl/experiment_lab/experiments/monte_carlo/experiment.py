"""The monte carlo experiment file."""

import logging
from typing import Any
import hydra
import numpy as np
import wandb
from experiment_lab.core.base_experiment import BaseExperiment
from experiment_lab.experiments.monte_carlo.components import (
    BaseSampler,
    BaseAggregator,
    BaseSampleFilter,
    BasePostProcessor,
)
from experiment_lab.experiments.monte_carlo.config import MCConfig


logger = logging.getLogger(__name__)


class MCExperiment(BaseExperiment):
    """The monte carlo experiment class."""

    def __init__(self, cfg: MCConfig) -> None:
        """The constructor for the monte carlo experiment."""
        self.cfg = cfg
        self.initialize_experiment()

    def initialize_experiment(self) -> None:
        """Initializes the monte carlo experiment config."""
        super().initialize_experiment()
        self.batch_size = (
            self.cfg.n_samples if self.cfg.batch_size is None else self.cfg.batch_size
        )

    def single_run(
        self, run_id: str, run_output_path: str, seed: int | None = None
    ) -> Any:
        """A single run of the monte carlo experiment.

        Args:
            run_id (str): The run id.
            run_output_path (str): The run output path.
            seed (int | None, optional): The initial random seed. Defaults to None.

        Returns:
            Any: The post processed results.
        """

        # Instantiate the required experiment components
        sampler: BaseSampler = hydra.utils.instantiate(self.cfg.sampler)
        aggregator: BaseAggregator = hydra.utils.instantiate(self.cfg.aggregator)
        sample_filter: BaseSampleFilter = hydra.utils.instantiate(
            self.cfg.sample_filter
        )
        post_processor: BasePostProcessor = hydra.utils.instantiate(
            self.cfg.post_processor
        )

        # Set the seed
        sampler.set_seed(seed=seed)

        # Sample, Filter, Aggregate, and Post Process, all while logging
        all_samples = None
        results = None
        for i in range(0, self.cfg.n_samples, self.batch_size):
            new_samples = sampler.sample(min(self.batch_size, self.cfg.n_samples - i))
            filtered_samples = sample_filter.filter_samples(new_samples)
            if all_samples is None:
                all_samples = filtered_samples
            else:
                all_samples = np.concatenate([all_samples, filtered_samples], axis=0)
            if self.cfg.aggregate_every_batch:
                if results is None:
                    results = []
                results.append(
                    post_processor.process(aggregator.aggregate(all_samples))
                )
                if self.cfg.wandb:
                    wandb.log(results[-1])
                if self.cfg.log_results:
                    logger.info(f"The current result is: {results[-1]}")
        if not self.cfg.aggregate_every_batch and all_samples is not None:
            results = post_processor.process(aggregator.aggregate(all_samples))
            if self.cfg.wandb:
                wandb.log(results)
            if self.cfg.log_results:
                logger.info(f"The current result is: {results}")
        return results
