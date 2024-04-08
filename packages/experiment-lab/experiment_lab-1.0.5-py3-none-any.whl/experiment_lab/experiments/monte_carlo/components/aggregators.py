"""Python file for the aggregators."""

import abc
from typing import Any, Callable, Dict
import hydra
import numpy as np


class BaseAggregator(abc.ABC):
    """The base aggregator class."""

    def __init__(self) -> None:
        """The constructor for a generic aggregator."""
        pass

    @abc.abstractmethod
    def aggregate(self, samples: np.ndarray) -> Any:
        """The aggregate function.

        Args:
            samples (np.ndarray): The samples to aggregate.

        Returns:
            Any: The aggregated result.
        """
        pass


class NpAggregator(BaseAggregator):
    """Aggregator to apply a numpy function to the axis=0 of the samples."""

    def __init__(self, np_func: Callable[..., np.ndarray] | str = np.mean) -> None:
        """The constructor of the NpAggregator that sets the np function to use.

        Args:
            np_func (Callable, optional): The np function to use. Defaults to np.mean.
        """
        super().__init__()
        if not isinstance(np_func, str):
            self.np_func: Callable[..., np.ndarray] = np_func
        else:
            self.np_func: Callable[..., np.ndarray] = hydra.utils.get_method(f"numpy.{np_func}")

    def aggregate(self, samples: np.ndarray) -> Any:
        """The aggregate function that applies the np function to the samples.

        Args:
            samples (np.ndarray): The samples.

        Returns:
            Any: The aggregated result.
        """
        return self.np_func(samples, axis=0)


class MultipleAggregators(BaseAggregator):
    """Aggregator to use multiple aggregators together."""

    def __init__(self, aggregators: Dict[str, BaseAggregator]) -> None:
        """Constructor for the aggregator to combine multiple aggregators.

        Args:
            aggregators (Dict[str, BaseAggregator]): The aggregators to combine.
        """
        super().__init__()
        self.aggregators = aggregators

    def aggregate(self, samples: np.ndarray) -> Dict[str, Any]:
        """Aggregates the samples using each aggregators and combines the results.

        Args:
            samples (np.ndarray): The samples to aggregate.

        Returns:
            Dict[str, Any]: The aggregated results.
        """
        return {k: v.aggregate(samples=samples) for k, v in self.aggregators.items()}
