"""Main entrypoint to run generic rl experiments."""

import minigrid

from experiment_lab.core.runner import run_experiment, root_config_folder
from experiment_lab.experiments.rl.experiment import RLExperiment
from experiment_lab.experiments.rl.config import RLConfig, register_configs

from functools import partial


run_rl_experiment = partial(
    run_experiment,
    experiment_cls=RLExperiment,
    config_cls=RLConfig,
    register_configs=register_configs,
    config_path=f"{root_config_folder}/rl",
)


if __name__ == "__main__":
    run_rl_experiment()
