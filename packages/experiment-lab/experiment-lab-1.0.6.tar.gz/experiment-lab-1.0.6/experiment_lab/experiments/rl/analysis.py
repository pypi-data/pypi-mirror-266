"""Runs the analysis for an rl experiment."""

from typing import Any, Dict

from pandas import DataFrame
from experiment_lab.core.base_analysis import BaseAnalysis
from experiment_lab.experiments.rl.config import RLConfig


class RLAnalysis(BaseAnalysis):
    """The class for analysis of rl experiments"""

    def __init__(self, cfg: RLConfig) -> None:
        """Initialization for rl analysis class

        Args:
            cfg (RLConfig): The rl config from the experiment.
        """
        self.cfg = cfg

    def analyze(self, df: DataFrame, configs: Dict[str, Dict[str, Any]]) -> Any:
        """The main analysis function for an rl experiment.

        Args:
            df (DataFrame): The run data from the experiments.
            configs (Dict[str, Dict[str, Any]]): The configs for each experiment.

        Returns:
            Any: The results of the analysis.
        """
        results = {
            "max_rewards": {
                experiment_id: {
                    "mean": df.loc[experiment_id]["rollout/ep_rew_mean"]
                    .groupby("run_id")
                    .max()
                    .mean(),
                    "std": df.loc[experiment_id]["rollout/ep_rew_mean"]
                    .groupby("run_id")
                    .max()
                    .std(),
                }
                for experiment_id in configs
            }
        }
        return results
