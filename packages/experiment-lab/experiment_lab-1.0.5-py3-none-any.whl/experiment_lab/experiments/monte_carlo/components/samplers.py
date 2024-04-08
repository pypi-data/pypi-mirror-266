"""Python file for the samplers."""

import abc
import numpy as np


class BaseSampler(abc.ABC):
    """The base sampler class."""

    def __init__(self) -> None:
        """Constructor for a generic sampler."""
        super().__init__()
        self.rng = np.random.default_rng()

    def set_seed(self, seed: int | None):
        """Sets the seed for the internal random number generator.

        Args:
            seed (int | None): The seed to set.
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed=seed)

    @abc.abstractmethod
    def sample(self, num_samples: int = 1) -> np.ndarray:
        """Samples a single point from the distribution represented by this sampler.

        Args:
            num_samples (int): The number of samples to generate.

        Returns:
            np.ndarray: The sample represented as a numpy array with shape (num_samples, ...)
        """
        pass


class UniformSampler(BaseSampler):
    """Samples from a uniform distribution"""

    def __init__(self, low: float = 1.0, high: float | None = None, k: int = 1) -> None:
        """Constructor for the uniform sampler.

        Args:
            low (float, optional): The minimum of the distribution to sample from (or maximum if high is left as None, in which case low is 0). Defualts to 1.0.
            high (float | None, optional): The maximum of the distribution to sample from. Defaults to None.
            k (int, optional): The number of random numbers per sample. Defaults to 1.
        """

        super().__init__()
        if high is None:
            self.low = 0
            self.high = low
        else:
            self.low = low
            self.high = high
        self.k = k

    def sample(self, num_samples: int = 1) -> np.ndarray:
        return self.rng.uniform(
            low=self.low, high=self.high, size=(num_samples, self.k)
        )
