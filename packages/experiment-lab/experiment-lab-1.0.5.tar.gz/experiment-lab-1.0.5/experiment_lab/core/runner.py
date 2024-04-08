"""File containing the main entrypoint function."""

import os

from typing import Any, Callable, Type, Sequence
import hydra
from omegaconf import DictConfig, OmegaConf

import experiment_lab
from experiment_lab.common.resolvers import register_resolvers
from experiment_lab.core.base_config import BaseConfig, register_configs
from experiment_lab.core.base_experiment import BaseExperiment

root_config_folder = f"{os.path.dirname(experiment_lab.__file__)}/configs"


def run_experiment(
    experiment_cls: Type[BaseExperiment],
    config_cls: Type[BaseConfig] = BaseConfig,
    register_configs: Callable[[], None] = register_configs,
    register_resolvers: Callable[[], None] = register_resolvers,
    config_path: str = root_config_folder,
    config_name: str = "config",
) -> Sequence[Any]:
    """The main entrypoint to collect all the hydra config and run the experiment.

    Args:
        experiment_cls (Type[BaseExperiment]): The experiment class.
        config_cls (Type[BaseConfig], optional): The config class. Defaults to BaseConfig.
        register_configs (Callable[[], None], optional): The function to register any configs. Defaults to register_configs.
        register_resolvers (Callable[[], None], optional): The function to register any resolvers. Defaults to register_resolvers.
        config_path (str, optional): The config path. Defaults to "./configs".
        config_name (str, optional): The default config name. Defaults to "config".

    Returns:
        Sequence[Any]: The list of results from the runs.
    """
    register_resolvers()
    register_configs()

    config_path = os.path.join(os.getcwd(), config_path)

    @hydra.main(config_path=config_path, config_name=config_name, version_base=None)
    def main(dict_cfg: DictConfig) -> Sequence[Any]:
        OmegaConf.resolve(dict_cfg)
        cfg: config_cls = OmegaConf.to_object(dict_cfg)  # type: ignore
        e = experiment_cls(cfg)
        return e.run()

    return main()
