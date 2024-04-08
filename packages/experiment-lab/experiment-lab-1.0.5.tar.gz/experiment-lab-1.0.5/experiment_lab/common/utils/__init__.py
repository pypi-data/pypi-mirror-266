"""A python module for utilities functions."""

import collections.abc
from typing import Any, Callable, Dict
import time
import logging
import re

logger = logging.getLogger(__name__)


def default(val: Any, d: Any, null_val: Any = None) -> Any:
    """Defaults a value to something when it matches a null_val.

    Args:
        val (Any): The original value.
        d (Any): The value to set if val == null_val.
        null_val (Any, optional): The null value. Defaults to None.

    Returns:
        Any: The value defaulting to the chosen default.
    """
    return val if val != null_val else d


def deep_update(d: Dict[Any, Any], u: collections.abc.Mapping) -> Dict[Any, Any]:
    """Deep update for dictionaries.

    Args:
        d (Dict[Any, Any]): The initial dictionary.
        u (collections.abc.Mapping): The mapping to update the initial dictionary with.

    Returns:
        Dict[Any, Any]: The updated dictionary.
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def time_f(f: Callable) -> Callable:
    def g(*args, **kwargs):
        logger.info(f"Start {f.__name__}")
        start_ns = time.time_ns()
        result = f(*args, **kwargs)
        end_ns = time.time_ns()
        logger.info(f"End {f.__name__}. Time Elapsed: {(end_ns - start_ns) / 1e9}s")
        return result

    return g

def camel_to_snake_case(s: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
