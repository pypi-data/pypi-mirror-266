"""Created an example mc experiment (goes with estimate_py.yaml) to show the usage of the mc experiments."""

import logging
from typing import Dict
import numpy as np

from experiment_lab.experiments.monte_carlo import UniformSampler, BasePostProcessor

logger = logging.getLogger(__name__)


class RandomPointInCircle(UniformSampler):
    """Sampler class to sample from a bernoulli distribution with p=\\pi / 4."""

    def __init__(self) -> None:
        """Constructor for RandomPointInCircle sampler."""
        super().__init__(low=0, high=1, k=2)

    def sample(self, num_samples: int = 1) -> np.ndarray:
        """Samples random points from the box between the points (0, 0) and (1, 1) and then checks if they within the circle with radius 1 centered at the origin.

        Args:
            num_samples (int, optional): The number of samples. Defaults to 1.

        Returns:
            np.ndarray: The binary samples.
        """
        return (np.linalg.norm(super().sample(num_samples), axis=1) < 1).astype(int)


class MultiplyByFour(BasePostProcessor):
    """A post processing class to multiply the mean by four to get the pi estimate."""

    def __init__(self) -> None:
        """Constructor for MultiplyByFour post processor."""
        super().__init__()

    def process(self, result: Dict[str, float]) -> Dict[str, float]:
        """Post processing function that takes the results from the multi aggregator and calculates the pi estimate (multiply by 4).

        Args:
            result (Dict[str, float]): The aggregated result with the mean in it.

        Returns:
            Dict[str, float]: The result containing the pi estimate and everything else in it.
        """
        return {"pi_estimate": result["mean"] * 4, **result}
