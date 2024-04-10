"""A python module a bunch of network building blocks."""

from typing import Any, Dict
import torch
from torch import nn


class Convolution(nn.Module):
    """Convolution block."""

    def __init__(
        self,
        conv_kwargs: Dict[str, Any],
        max_pooling_kwargs: Dict[str, Any],
        nd: int = 2,
    ) -> None:
        """Constructor for convolution block taking the conv kwargs and pool kwargs.

        Args:
            conv_kwargs (Dict[str, Any]): The kwargs for the torch convolution layer.
            max_pooling_kwargs (Dict[str, Any]): The kwargs for the torch max pooling layer.
            nd (int, optional): The number of dimensions to convolve over. Defaults to 2.

        Raises:
            ValueError: When nd is not 1, 2, or 3.
        """
        super().__init__()
        self.nd = nd
        if self.nd == 1:
            self.conv = nn.Conv1d(**conv_kwargs)
        elif self.nd == 2:
            self.conv = nn.Conv2d(**conv_kwargs)
        elif self.nd == 3:
            self.conv = nn.Conv3d(**conv_kwargs)
        else:
            raise ValueError("nd must be 1, 2, or 3 for convolution block.")

        if self.nd == 1:
            self.pool = nn.MaxPool1d(**max_pooling_kwargs)
        elif self.nd == 2:
            self.pool = nn.MaxPool2d(**max_pooling_kwargs)
        elif self.nd == 3:
            self.pool = nn.MaxPool3d(**max_pooling_kwargs)
        else:
            raise ValueError("nd must be 1, 2, or 3 for convolution block.")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """The forward function on the convolution block.

        Args:
            x (torch.Tensor): The input.

        Returns:
            torch.Tensor: The output.
        """
        return self.pool(self.conv(x))
