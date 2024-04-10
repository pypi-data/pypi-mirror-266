"""Python file for the post proessors"""

from typing import Any, Dict
import abc


class BasePostProcessor(abc.ABC):
    """The base post processor class."""

    def __init__(self) -> None:
        """The constructor for a generic post processor."""
        super().__init__()

    @abc.abstractmethod
    def process(self, result: Any) -> Dict[str, Any]:
        """Applies post processing on the aggregated result.

        Args:
            result (Any): The aggregated result.

        Returns:
            Any: The post processed result (publishable to wandb with names).
        """
        pass


class PassThroughPostProcessor(BasePostProcessor):
    """The pass through post processor."""

    def __init__(self) -> None:
        """The constructor for the pass through post processor."""
        super().__init__()

    def process(self, result: Any) -> Dict[str, Any]:
        """Returns the passed in result.

        Args:
            result (Any): The aggregated result.

        Returns:
            Any: The same result wrapped in a dict.
        """
        return {"result": result}
