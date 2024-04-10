"Random wait experiment python file."
import time
import numpy as np
import wandb
import logging

from experiment_lab.core.base_config import BaseConfig
from experiment_lab.core.base_experiment import BaseExperiment
from experiment_lab.core.runner import run_experiment

logger = logging.getLogger(__name__)


class RandomWaits(BaseExperiment):
    """The random wait experiment class."""

    def __init__(self, cfg: BaseConfig) -> None:
        """The constructor for the random wait experiment

        Args:
            cfg (BaseConfig): The experiment configuration.
        """
        assert type(cfg) == BaseConfig
        super().__init__(cfg)

    def single_run(
        self, run_id: str = "", run_output_path: str = "", seed: int | None = None
    ) -> None:
        """Runs the trivial random wait experiment a single time with one seed.

        Args:
            run_id (str, optional): The run id. Defaults to "".
            seed (int | None, optional): The seed. Defaults to None.

        Returns:
            Any: Any resulting metrics
        """
        logger.info("Starting")
        rng = np.random.default_rng(seed=seed)
        num = rng.integers(10)
        if self.cfg.wandb:
            wandb.log({"num": num})
        time.sleep(num)
        logger.info("Done!")


if __name__ == "__main__":
    run_experiment(experiment_cls=RandomWaits)
