"""A python module containing a basic MLP network function."""

from typing import Any, Dict, Sequence, Type
from torch import nn
from experiment_lab.common.networks.network import create_network


def create_mlp_network(
    layer_sizes: Sequence[int],
    linear_layer_cls: Type[nn.Module] = nn.Linear,
    constant_layer_kwargs: Dict[str, Any] | None = None,
    layer_activations: nn.Module | Sequence[nn.Module | None] | None = None,
    final_activation: nn.Module | None = None,
    dropout_p: Sequence[float | None] | float | None = None,
) -> nn.Module:
    """A create multi layer percetron function.

    Args:
        layer_sizes (Sequence[int]): The layer sizes to use in the network.
        linear_layer_cls (Type[nn.Module], optional): The linear layer class to use. Defaults to nn.Linear.
        layer_activations (nn.Module | Sequence[nn.Module  |  None] | None, optional): The layer activation funcitons.. Defaults to None.
        final_activation (nn.Module | None, optional): The final activation function before the output. Defaults to None.
        dropout_p (Sequence[float  |  None] | float | None, optional): The probability of dropout per layer.. Defaults to None.

    Returns:
        nn.Module: The mlp network.
    """
    assert (
        len(layer_sizes) >= 2
    ), "Layer sizes must be at least 2 to include at least one layer in the network."
    return create_network(
        layer_cls=linear_layer_cls,
        n_layers=len(layer_sizes) - 1,
        layer_kwargs=[
            dict(in_features=layer_sizes[i], out_features=layer_sizes[i + 1])
            for i in range(len(layer_sizes) - 1)
        ],
        constant_layer_kwargs=constant_layer_kwargs,
        layer_activations=layer_activations,
        final_activation=final_activation,
        dropout_p=dropout_p,
    )
