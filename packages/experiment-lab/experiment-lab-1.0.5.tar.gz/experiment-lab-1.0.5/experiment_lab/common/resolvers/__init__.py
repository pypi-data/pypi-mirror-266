"""Hydra config resolvers."""

from omegaconf import OmegaConf
from inspect import isfunction

from experiment_lab.common.resolvers.list_resolvers import (
    dup,
    wrap_around,
    toggle,
    range,
    arange,
    linspace,
)
from experiment_lab.common.resolvers.object_resolvers import (
    get_class,
    get_object,
    get_method,
)


def register_resolvers() -> None:
    """Registers the resolvers imported to this file."""
    ignores = set(["register_resolvers", "isfunction"])

    resolvers = {
        k: v for k, v in globals().items() if k not in ignores and isfunction(v)
    }

    for k, v in resolvers.items():
        OmegaConf.register_new_resolver(k, v)
