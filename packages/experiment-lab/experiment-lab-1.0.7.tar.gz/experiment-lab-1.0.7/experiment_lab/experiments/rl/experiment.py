"""The rl experiment python file."""

import os
from typing import Any, List, Type, Dict
import gymnasium as gym
import hydra
import torch
from wandb.integration.sb3 import WandbCallback

from stable_baselines3.common.callbacks import CallbackList
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.policies import BasePolicy
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import VecVideoRecorder


from experiment_lab.core.base_experiment import BaseExperiment
from experiment_lab.experiments.rl.config import RLConfig
from experiment_lab.experiments.rl.environment import GeneralVecEnv
from experiment_lab.common.utils import default


class RLExperiment(BaseExperiment):
    """The rl experiment class."""

    def __init__(self, cfg: RLConfig) -> None:
        """Constructor for rl experiment.

        Args:
            cfg (RLConfig): The config to run the experiment with.
        """
        self.cfg = cfg
        self.initialize_experiment()

    def initialize_experiment(self) -> None:
        """Initializes the rl experiment"""
        super().initialize_experiment()

        self.wrapper_cls_lst: List[Type[gym.Wrapper]] = (
            []
            if self.cfg.wrapper_cls_lst is None
            else [
                hydra.utils.get_class(wrapper_cls)
                for wrapper_cls in self.cfg.wrapper_cls_lst
            ]
        )
        self.policy_cls: Type[BasePolicy] = hydra.utils.get_class(self.cfg.policy_cls)
        self.callback_cls_lst: List[Type[BaseCallback]] = (
            []
            if self.cfg.callback_cls_lst is None
            else [
                hydra.utils.get_class(callback_cls)
                for callback_cls in self.cfg.callback_cls_lst
            ]
        )

        self.wrapper_kwargs_lst: List[Dict[str, Any]] = default(
            self.cfg.wrapper_kwargs_lst, []
        )
        for _ in range(len(self.wrapper_kwargs_lst), len(self.wrapper_cls_lst)):
            self.wrapper_kwargs_lst.append({})

        self.callback_kwargs_lst: List[Dict[str, Any]] = default(
            self.cfg.callback_kwargs_lst, []
        )
        for _ in range(len(self.callback_kwargs_lst), len(self.callback_cls_lst)):
            self.callback_kwargs_lst.append({})

        self.model_kwargs: Dict[str, Any] = default(self.cfg.model_kwargs, {})

        self.transfer_steps: List[int] = default(self.cfg.transfer_steps, [])

        self.device: torch.device = torch.device(self.cfg.device)

        self.additional_wandb_init_kwargs["sync_tensorboard"] = True
        self.additional_wandb_init_kwargs["save_code"] = True
        if self.cfg.record_policy_videos:
            self.additional_wandb_init_kwargs["monitor_gym"] = True

    def single_run(
        self, run_id: str, run_output_path: str, seed: int | None = None
    ) -> Any:
        """A single run of the rl experiment.

        Args:
            run_id (str): The run id.
            run_output_path (str): The run output path.
            seed (int | None, optional): The initial seed.. Defaults to None.

        Returns:
            Any: Any resulting metrics.
        """

        # Setup the device to train on
        if self.cfg.gpu_idx is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(self.cfg.gpu_idx)

        # Create the environment
        env = GeneralVecEnv(
            env_config=self.cfg.env_config,
            transfer_steps=self.cfg.transfer_steps,
            wrappers=self.wrapper_cls_lst,
            wrapper_kwargs_lst=self.cfg.wrapper_kwargs_lst,
            n_envs=self.cfg.n_envs,
            seed=seed,
            monitor_dir=self.cfg.monitor_dir,
            monitor_kwargs=self.cfg.monitor_kwargs,
            start_method=self.cfg.start_method,
            render_mode=(
                "rgb_array" if self.cfg.record_policy_videos else self.cfg.render_mode
            ),
        )
        if self.cfg.record_policy_videos:
            env = VecVideoRecorder(
                env,
                f"./wandb/videos/{run_id}",
                record_video_trigger=lambda x: x
                % (self.cfg.video_freq // self.cfg.n_envs)
                == 0,
                video_length=self.cfg.video_length,
                name_prefix=self.cfg.video_name_prefix,
            )

        env.seed(seed)
        env.reset()

        # Setup the model
        model = hydra.utils.instantiate(
            {
                "_target_": self.cfg.model_cls,
            },
            env=env,
            policy=self.policy_cls,
            policy_kwargs=self.cfg.policy_kwargs,
            device=self.device,
            tensorboard_log=f"./logs/" if self.cfg.log else None,
            verbose=self.cfg.verbose,
            **self.model_kwargs,
        )
        model.set_random_seed(seed)
        model_save_path = f"{run_output_path}/models/"

        # Instantiate the callbacks
        callback_instances = []
        if (
            self.cfg.log
            and self.cfg.wandb
            and self.cfg.wandb_callback_kwargs is not None
        ):
            callback_instances.append(
                WandbCallback(
                    gradient_save_freq=self.cfg.wandb_callback_kwargs.gradient_save_freq,
                    model_save_freq=self.cfg.wandb_callback_kwargs.model_save_freq,
                    model_save_path=model_save_path,
                    verbose=self.cfg.verbose,
                )
            )
        for callback_cls, callback_kwargs in zip(
            self.callback_cls_lst, self.callback_kwargs_lst
        ):
            callback_instances.append(
                callback_cls(**hydra.utils.instantiate(callback_kwargs))
            )

        # Run the algorithm
        model.learn(
            total_timesteps=self.cfg.total_time_steps,
            log_interval=self.cfg.log_interval,
            tb_log_name=run_id,
            callback=(
                CallbackList(callback_instances)
                if len(callback_instances) > 0
                else None
            ),
        )

        env.close()

        if self.cfg.save_model:
            os.makedirs(model_save_path, exist_ok=True)
            model.save(f"{model_save_path}/final.zip")
