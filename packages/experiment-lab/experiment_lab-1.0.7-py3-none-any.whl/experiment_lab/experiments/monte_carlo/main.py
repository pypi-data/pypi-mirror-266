"""Main entrypoint to run generic monte carlo experiments."""

from experiment_lab.core.runner import run_experiment, root_config_folder
from experiment_lab.experiments.monte_carlo.experiment import MCExperiment
from experiment_lab.experiments.monte_carlo.config import MCConfig, register_configs

from functools import partial


run_mc_experiment = partial(
    run_experiment,
    experiment_cls=MCExperiment,
    config_cls=MCConfig,
    register_configs=register_configs,
    config_path=f"{root_config_folder}/mc",
)


if __name__ == "__main__":
    run_mc_experiment()
