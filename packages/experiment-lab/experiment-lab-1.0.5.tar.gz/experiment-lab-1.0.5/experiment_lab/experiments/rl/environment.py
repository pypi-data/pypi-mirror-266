"""The environment wrapper for gym to run the rl experiment."""

from typing import Any, List, SupportsFloat, Tuple, Dict, Type

import os

import gymnasium as gym
from gymnasium.core import RenderFrame
from gymnasium.envs.registration import EnvSpec
import hydra
import numpy as np
import multiprocessing as mp

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.vec_env.base_vec_env import VecEnvStepReturn


class ListEnv(gym.Env):
    """An environment for maintaining multiple transfers."""

    def __init__(self, env_lst: List[gym.Env]) -> None:
        """The constructor for the list env class.

        Args:
            env_lst (List[gym.Env]): The list of environments to use.
        """
        self.env_lst = env_lst
        self.env_idx = 0

    def incr_env_idx(self) -> bool:
        """Increments the environment to the next

        Returns:
            bool: Whether or not an environment switch occured.
        """
        if self.env_idx >= len(self.env_lst) - 1:
            return False
        self.cur_env.close()
        self.env_idx += 1
        self.cur_env.reset()
        return True

    def step(
        self, action: Any
    ) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        """Steps through the current environment.

        Args:
            action (Any): The action to take

        Returns:
            Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]: The step output.
        """
        return self.cur_env.step(action=action)

    def reset(
        self, *, seed: int | None = None, options: Dict[str, Any] | None = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """Resets the current environment.

        Args:
            seed (int | None, optional): The seed to use. Defaults to None.
            options (Dict[str, Any] | None, optional): The options to use. Defaults to None.

        Returns:
            Tuple[Any, Dict[str, Any]]: The observation and info in the reset environment.
        """
        return self.cur_env.reset(seed=seed, options=options)

    def render(self) -> RenderFrame | List[RenderFrame] | None:
        """Renders the current environment.

        Returns:
            RenderFrame | List[RenderFrame] | None: The render return.
        """
        return self.cur_env.render()

    def close(self):
        """Closes all the environments."""
        for env in self.env_lst:
            env.close()

    @property
    def cur_env(self) -> gym.Env:
        """Gets the current environment.

        Returns:
            gym.Env: The current environment.
        """
        return self.env_lst[self.env_idx]

    @property
    def unwrapped(self) -> gym.Env:
        """Returns the base non-wrapped environment.

        Returns:
            Env: The base non-wrapped :class:`gymnasium.Env` instance
        """
        return self.cur_env.unwrapped

    @property
    def action_space(self) -> gym.Space:
        """Returns the action space of the current environment.

        Returns:
            gym.Space: The action space.
        """
        return self.cur_env.action_space

    @property
    def observation_space(self) -> gym.Space:
        """Returns the observation space of the current environment.

        Returns:
            gym.Space: The observation space.
        """
        return self.cur_env.observation_space

    @property
    def reward_range(self) -> Tuple[float, float]:
        """The reward range of the environment.

        Returns:
            Tuple[float, float]: The reward range.
        """
        return self.cur_env.reward_range

    @property
    def spec(self) -> EnvSpec | None:
        return self.cur_env.spec

    @property
    def np_random(self) -> np.random.Generator:
        """The np_random generator of the current env.

        Returns:
            np.random.Generator: The generator.
        """
        return self.cur_env.np_random

    @property
    def render_mode(self) -> str | None:
        """The render mode of the current environment.

        Returns:
            str | None: The render mode.
        """
        return self.cur_env.render_mode


class GeneralVecEnv(SubprocVecEnv):
    """A full vec env wrapper around gym envs for easy construction and configuration."""

    def __init__(
        self,
        env_config: Dict[str, Any],
        transfer_steps: List[int] | None = None,
        wrappers: List[Type[gym.Wrapper]] | None = [],
        wrapper_kwargs_lst: List[Dict[str, Any]] | None = [],
        n_envs: int = 1,
        seed: int | None = None,
        monitor_dir: str | None = None,
        monitor_kwargs: Dict[str, Any] | None = None,
        start_method: str | None = None,
        render_mode: str | None = None,
    ) -> None:
        """Constructor for general vec env wrapper for the rl experiment module.

        Args:
            env_config (Dict[str, Any]): The environment config to use.
            transfer_steps (List[int] | None, optional): The number of steps to run before each transfer specified in the environment config. Defaults to None.
            wrappers (List[Type[gym.Wrapper]] | None, optional): The wrappers to apply to the env. Defaults to [].
            wrapper_kwargs_lst (List[Dict[str, Any]] | None, optional): The kwargs for the wrappers. Defaults to [].
            n_envs (int, optional): The number of envs to run in parallel. Defaults to 1.
            seed (int | None, optional): The seed to use. Defaults to None.
            monitor_dir (str | None, optional): The directory to save monitor logs to. Defaults to None.
            monitor_kwargs (Dict[str, Any] | None, optional): The kwargs for the monitor. Defaults to None.
            start_method (str | None, optional): The start method used for multiprocessing envs. Defaults to None.
            render_mode (str | None, optional): The render mode of the environment. Defaults to None.
        """

        self.n_tasks = max(
            (len(env_config[k]) if type(env_config[k]) == list else 1)
            for k in env_config
        )
        env_configs = []
        for i in range(self.n_tasks):
            env_configs.append(
                {
                    k: ((v[i] if i < len(v) else v[-1]) if type(v) == list else v)
                    for k, v in env_config.items()
                }
            )

        for cfg in env_configs:
            if isinstance(cfg["env_id"], str) and cfg["env_id"] not in gym.registry:
                cfg["env_id"] = hydra.utils.get_class(cfg["env_id"])

        env_spec_mapping = {
            cfg["env_id"]: gym.registry[cfg["env_id"]]
            for cfg in env_configs
            if type(cfg["env_id"]) == str
        }

        self.n_envs = n_envs
        self.transfer_steps = [] if transfer_steps is None else transfer_steps

        self.total_time_steps = 0
        self.last_incr = 0
        self.cur_env_idx = 0

        monitor_kwargs = {} if monitor_kwargs is None else monitor_kwargs

        wrappers = [] if wrappers is None else wrappers
        wrapper_kwargs_lst = [] if wrapper_kwargs_lst is None else wrapper_kwargs_lst
        for _ in range(len(wrapper_kwargs_lst), len(wrappers)):
            wrapper_kwargs_lst.append({})

        def make_env_fn(rank):
            def _make_env(config):
                env_id = config["env_id"]
                env_kwargs = hydra.utils.instantiate(
                    {k: v for k, v in config.items() if k != "env_id"}
                )

                # Initialize the environment
                if isinstance(env_id, str):
                    env: gym.Env = gym.make(
                        env_spec_mapping[env_id], render_mode=render_mode, **env_kwargs
                    )
                else:
                    env: gym.Env = env_id(**env_kwargs, render_mode=render_mode)

                # Optionally use the random seed provided
                if seed is not None:
                    env.np_random = np.random.default_rng(seed=seed + rank)
                    env.action_space.seed(seed + rank)

                # Wrap the env in a Monitor wrapper
                # to have additional training information
                monitor_path = (
                    os.path.join(monitor_dir, str(rank))
                    if monitor_dir is not None
                    else None
                )
                # Create the monitor folder if needed
                if monitor_path is not None:
                    os.makedirs(monitor_path, exist_ok=True)
                env = Monitor(
                    env,
                    filename=monitor_path,
                    **hydra.utils.instantiate(monitor_kwargs),
                )

                # Wrap the environment with the provided wrappers
                for wrapper_cls, wrapper_kwargs in zip(wrappers, wrapper_kwargs_lst):
                    env = wrapper_cls(env, **hydra.utils.instantiate(wrapper_kwargs))

                return env

            def _init() -> gym.Env[Any, Any]:
                # Returns a list env with each env constructed from the config in env_configs
                return ListEnv([_make_env(config) for config in env_configs])

            return _init

        env_fns = [make_env_fn(rank=i) for i in range(n_envs)]

        if start_method is None:
            start_method = "spawn" if "spawn" in mp.get_all_start_methods() else None

        super().__init__(env_fns=env_fns, start_method=start_method)

    def step_wait(self) -> VecEnvStepReturn:
        """Waits for the results of the step call and incremenets the environment idx if needed.

        Returns:
            VecEnvStepReturn: The step return.
        """
        observations, rewards, dones, infos = super().step_wait()
        # Increment total time steps
        self.total_time_steps += self.n_envs
        if (
            self.cur_env_idx < len(self.transfer_steps)
            and self.total_time_steps - self.last_incr
            > self.transfer_steps[self.cur_env_idx]
        ):
            self.last_incr = self.total_time_steps
            # Trigger the novelty if enough steps have passed
            transfer_injected: List[bool] = self.env_method("incr_env_idx")
            if np.any(transfer_injected):
                self.cur_env_idx += 1
                dones[:] = True

        return observations, rewards, dones, infos
