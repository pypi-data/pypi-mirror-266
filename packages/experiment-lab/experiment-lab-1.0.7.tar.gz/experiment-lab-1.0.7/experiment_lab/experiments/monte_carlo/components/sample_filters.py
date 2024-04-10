"""Python file for sample filters."""

import abc
import numpy as np


class BaseSampleFilter(abc.ABC):
    """The base sample filter class."""

    def __init__(self) -> None:
        """Constructor for a generic sample filter."""
        super().__init__()

    @abc.abstractmethod
    def filter_samples(self, samples: np.ndarray) -> np.ndarray:
        """Filters the un-aggregated samples.

        Args:
            samples (np.ndarray): The un-aggregated un-filtered samples.

        Returns:
            np.ndarray: The un-aggregated filtered samples.
        """
        pass


class PassThroughSampleFilter(BaseSampleFilter):
    """The pass through sample filter class."""

    def __init__(self) -> None:
        """Constructor for pass through sample filter."""
        super().__init__()

    def filter_samples(self, samples: np.ndarray) -> np.ndarray:
        """Returns the full sample list.

        Args:
            samples (np.ndarray): The samples.

        Returns:
            np.ndarray: The samples.
        """
        return samples
