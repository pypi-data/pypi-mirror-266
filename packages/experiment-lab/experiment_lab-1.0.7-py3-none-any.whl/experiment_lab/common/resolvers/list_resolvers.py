"""List resolvers for easily generating lists in config files"""

from typing import Any, Callable, Sequence
import numpy as np


def wrap_f(f: Callable):
    """Wraps function and converts output to list.

    Args:
        f (Callable): The function to wrap.
    """

    def g(*args, **kwargs) -> Sequence[Any]:
        return list(f(*args, **kwargs))

    return g


def dup(n: int, x: Any) -> Sequence[Any]:
    """Duplicates x into a list of length n.

    Args:
        n (int): The length of the resulting list.
        x (Any): The value to duplicate.

    Returns:
        Sequence[Any]: The list containing x, n times.
    """
    return [x for _ in range(n)]


def wrap_around(n: int, lst: Sequence[Any]) -> Sequence[Any]:
    """Generates a list of length n by iterating through lst and wrapping around if the values run out.

    Args:
        n (int): The length of the resulting list.
        lst (Sequence[Any]): The list to iterate through.

    Returns:
        Sequence[Any]: The list wrapping around lst.
    """
    return [lst[i % len(lst)] for i in range(n)]


def toggle(n: int, fst: Any = False, snd: Any = True) -> Sequence[Any]:
    """Toggles between two values until a list of length n is generated.

    Args:
        n (int): The length of the resulting list.
        fst (Any, optional): The first (and third, fifth, ...) value to use. Defaults to False.
        snd (Any, optional): The second (and fourth, sixth, ...) value to use. Defaults to True.

    Returns:
        Sequence[Any]: The resulting list toggling between the two values.
    """
    return wrap_around(n=n, lst=[fst, snd])


range = wrap_f(range)
arange = wrap_f(np.arange)
linspace = wrap_f(np.linspace)
