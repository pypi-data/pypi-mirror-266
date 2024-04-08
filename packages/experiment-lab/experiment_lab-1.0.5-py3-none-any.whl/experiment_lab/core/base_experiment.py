"""The file to hold the base experiment code."""

from dataclasses import asdict
from typing import Any, Sequence, Tuple

import abc
import os
import logging
import multiprocessing as mp
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf
import wandb
import time
import glob
import pickle as pkl

from experiment_lab.common.utils import time_f, camel_to_snake_case
from experiment_lab.core.base_config import BaseConfig, NRunMethodEnum

logger = logging.getLogger(__name__)


class BaseExperiment(abc.ABC):
    """A generic base experiment class for all experiments to inherit from."""

    INCR_SEED_BY = 12

    def __init__(self, cfg: BaseConfig) -> None:
        """The constructor for the base experiment class."""
        self.cfg = cfg
        self.initialize_experiment()

    def initialize_experiment(self) -> None:
        """Initializes the experiment that is about to get run."""
        self.wandb_dict_config = asdict(self.cfg)
        if self.cfg.experiment_name:
            self.experiment_name = self.cfg.experiment_name
        else:
            self.experiment_name = (
                f"{camel_to_snake_case(self.__class__.__name__.lower())}"
            )
        self.timestamp = int(time.time())
        self.experiment_id = f"{self.experiment_name}_{self.timestamp}"
        self.output_directory = HydraConfig.get().runtime.output_dir
        self.additional_wandb_init_kwargs = {}

    @abc.abstractmethod
    def single_run(
        self, run_id: str, run_output_path: str, seed: int | None = None
    ) -> Any:
        """The entrypoint to the experiment.

        Args:
            run_id (str): The a unique string id for the run.
            run_output_path (str): The path to output or save anything for the run.
            seed (int | None, optional): The random seed to use for the experiment run. Defaults to None.

        Returns:
            Any: The results from this experiment run.
        """
        pass

    def _single_run_wrapper(
        self, intial_seed_and_run_num: Tuple[int | None, int] = (None, 0)
    ) -> Any:
        """A wrapper for the single run call to do run specific setup and post processing.

        Args:
            intial_seed_and_run_num (Tuple[int  |  None, int], optional): A tuple with both the seed and the run number. Defaults to (None, 0).

        Returns:
            Any: The results from the experiment run.
        """
        seed, run_num = intial_seed_and_run_num
        seed = None if seed is None else seed + run_num * BaseExperiment.INCR_SEED_BY
        logger.info(f"Starting individual run with seed {seed}")
        start_ns = time.time_ns()
        wandb_run = None
        run_id = f"{self.experiment_id}_{run_num}_{self.cfg.n_runs}"
        run_output_path = f"{self.output_directory}/{run_id}"
        os.makedirs(run_output_path, exist_ok=True)

        if self.cfg.wandb:
            wandb_run = wandb.init(
                id=run_id,
                config={
                    **self.wandb_dict_config,
                    "experiment_name": self.experiment_name,
                    "timestamp": self.timestamp,
                    "experiment_id": self.experiment_id,
                    "experiment_cls": self.__class__.__name__.lower(),
                },
                reinit=True,
                settings=wandb.Settings(start_method="thread"),
                **self.additional_wandb_init_kwargs,
                **self.cfg.wandb,
            )
        result = self.single_run(
            run_id=run_id, run_output_path=run_output_path, seed=seed
        )
        if result is not None:
            with open(f"{run_output_path}/result.pkl", "wb") as f:
                pkl.dump(result, f)
        end_ns = time.time_ns()
        logger.info(
            f"Finished run with seed {seed}. Time elapsed: {(end_ns - start_ns) / 1e9}s"
        )
        if wandb_run is not None:

            def save_folder(folder_path, base_path):
                for p in glob.glob(f"{folder_path}/**", recursive=True):
                    if os.path.isfile(p):
                        wandb_run.save(p, base_path=base_path, policy="end")

            save_folder(folder_path=run_output_path, base_path=run_output_path)
            save_folder(
                folder_path=f"{self.output_directory}/.hydra",
                base_path=self.output_directory,
            )
            wandb_run.finish()
        return result

    @time_f
    def run(self) -> Sequence[Any]:
        """Runs the experiment multiple times in series and aggregates the results.

        Args:
            n_runs (int, optional): The number of times to run the experiment. Defaults to 1.
            seed (int | None, optional): The initial seed of the first experiment run. The seeds of further experiment runs increment by 1 each run. Defaults to None.

        Returns:
            Sequence[Any]: The list of results from the runs.
        """
        results = None
        if self.cfg.n_runs <= 1 or self.cfg.n_run_method == NRunMethodEnum.series:
            results = [
                self._single_run_wrapper((self.cfg.seed, run_num))
                for run_num in range(self.cfg.n_runs)
            ]
        elif self.cfg.n_run_method == NRunMethodEnum.parallel:
            with mp.Pool() as pool:
                results = pool.map(
                    func=self._single_run_wrapper,
                    iterable=[
                        (self.cfg.seed, run_num) for run_num in range(self.cfg.n_runs)
                    ],
                )
        assert results is not None, "Unknown n_run_method!"
        return results
