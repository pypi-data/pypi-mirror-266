"""Python file containing the configs for rl experiments."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from hydra.core.config_store import ConfigStore

from experiment_lab.core.base_config import BaseConfig


@dataclass
class WandbCallbackConfig:
    """The wandb callback config dataclass."""

    model_save_freq: int = 1_000
    gradient_save_freq: int = 0


@dataclass
class RLConfig(BaseConfig):
    """The RL Config dataclass."""

    env_config: Dict[str, Any] = field(
        default_factory=lambda: {"env_id": "CartPole-v1"}
    )
    transfer_steps: List[int] | None = None

    total_time_steps: int = 10_000
    n_envs: int = 1

    wrapper_cls_lst: List[str] | None = None
    wrapper_kwargs_lst: List[Dict[str, Any]] | None = None

    model_cls: str = "stable_baselines3.PPO"
    model_kwargs: Dict[str, Any] | None = None

    policy_cls: str = "stable_baselines3.ppo.MlpPolicy"
    policy_kwargs: Dict[str, Any] | None = None

    callback_cls_lst: List[str] | None = None
    callback_kwargs_lst: List[Dict[str, Any]] | None = None
    wandb_callback_kwargs: WandbCallbackConfig | None = field(
        default_factory=WandbCallbackConfig
    )

    verbose: int = 1

    monitor_dir: str | None = None
    monitor_kwargs: Dict[str, Any] | None = None

    record_policy_videos: bool = False
    video_length: int = 200
    video_freq: int = 5000
    video_name_prefix: str = "agent"

    start_method: str | None = None
    render_mode: str | None = None

    log: bool = True
    log_interval: int = 1
    save_model: bool = True

    device: str = "mps"
    gpu_idx: int | None = None


def register_configs():
    """Registers the rl config."""
    cs = ConfigStore.instance()
    cs.store(name="wandb_callback_defaults", node=WandbCallbackConfig)
    cs.store(name="rl_config", node=RLConfig)
