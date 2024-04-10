"""Helper functions to analyze the results of experiments."""

import abc
from textwrap import indent
from typing import Any, Dict, Tuple
import pandas as pd
import wandb
import tqdm
import logging

from experiment_lab.core.base_config import BaseConfig


logger = logging.getLogger(__name__)

api = None


def get_api_instance() -> wandb.Api:
    """Gets an instance of the wandb api.

    Returns:
        wandb.Api: The wandb api instance.
    """
    global api
    if api is None:
        api = wandb.Api()
    return api


class BaseAnalysis(abc.ABC):
    """A generic base experiment analysis class."""

    def __init__(self, cfg: BaseConfig) -> None:
        """The constructor for the BaseAnalysis class.

        Args:
            cfg (BaseConfig): The config to analyze with.
        """
        self.cfg = cfg

    def load_data(self) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
        """Function to load the run data of an experiment.

        Raises:
            ValueError: If wandb config is not specified, raise a ValueError.

        Returns:
            Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]: The dataframe containing all the run data and the dict containing all the configs.
        """
        if self.cfg.wandb is None:
            raise ValueError("Not wandb config specified")
        api = get_api_instance()
        wandb_runs = api.runs(
            path=self.cfg.wandb["project"],
            filters={
                "$and": [
                    {"state": "finished"},
                    {"config.experiment_name": self.cfg.experiment_name},
                ]
                + self.cfg.analysis.filters,
            },
            include_sweeps=False,
        )

        full_df = []

        configs = {}

        for wandb_run in tqdm.tqdm(wandb_runs):
            df = pd.DataFrame(
                wandb_run.scan_history(keys=self.cfg.analysis.wandb_keys),
            )
            df["experiment_id"] = wandb_run.config["experiment_id"]
            df["run_id"] = wandb_run.id
            if wandb_run.config["experiment_id"] not in configs:
                configs[wandb_run.config["experiment_id"]] = wandb_run.config
            if self.cfg.analysis.index is not None:
                df.set_index(
                    ["experiment_id", "run_id", self.cfg.analysis.index], inplace=True
                )
            else:
                df.set_index(["experiment_id", "run_id"], append=True, inplace=True)

            full_df.append(df)

        full_df = pd.concat(full_df)
        full_df.sort_index(inplace=True)

        return full_df, configs

    def _analyze_wrapper(self) -> Any:
        """A wrapper for the analyze function.

        Returns:
            Any: The results of the analysis.
        """
        df, configs = self.load_data()
        results = self.analyze(df=df, configs=configs)
        logger.info(results)
        return results

    @abc.abstractmethod
    def analyze(self, df: pd.DataFrame, configs: Dict[str, Dict[str, Any]]) -> Any:
        """Runs the analysis for the experiment.

        Args:
            df (pd.DataFrame): The results dataframe from wandb.
            configs (Dict[str, Dict[str, Any]]): The configs for each experiment.

        Returns:
            Any: The results of the analysis.
        """
        pass
