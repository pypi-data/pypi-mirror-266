from typing import List, Union

import uuid
from torch_geometric.nn.models import GCN

from aq_geometric.models.base_model import BaseModel


class GCNModel(BaseModel, GCN):
    r"""GCN model for predicting air quality.
    
    This basic GCN model implementation is a wrapper around the PyTorch Geometric
    implementation of the Graph Convolutional Network (GCN) model.
    
    Args:
        name (str): The name of the model.
        guid (str): The unique identifier for the model.
        stations (list): The list of stations to use for the model.
        in_channels (int): The number of input channels.
        hidden_channels (int): The number of hidden channels.
        num_layers (int): The number of layers.
        out_channels (int): The number of output channels.
        dropout (float): The dropout rate.
        act (Callable): The activation function.
        act_first (bool): Whether to apply the activation function first.
        act_kwargs (dict): The keyword arguments for the activation function.
        norm (Callable): The normalization function.
        norm_kwargs (dict): The keyword arguments for the normalization function.
        jk (str): The type of jump connection, if any.
        **kawrgs: Additional keyword arguments for `torch_geometric.nn.conv.GCNConv`.
    """
    def __init__(
        self,
        name: str = "GCNModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        features: List[str] = ["OZONE", "PM2.5", "NO2"],
        targets: List[str] = ["OZONE", "PM2.5", "NO2"],
        in_channels: int = 48,
        hidden_channels: int = 256,
        num_layers: int = 3,
        out_channels: int = 256,
        dropout: float = 0.5,
        act=None,
        act_first: bool = True,
        act_kwargs=None,
        norm=None,
        norm_kwargs=None,
        jk: str = "last",
    ):
        super().__init__(
            name=name,
            guid=guid,
            stations=stations,
            features=features,
            targets=targets,
            in_channels=in_channels,
            hidden_channels=hidden_channels,
            num_layers=num_layers,
            out_channels=out_channels,
            dropout=dropout,
            act=act,
            act_first=act_first,
            act_kwargs=act_kwargs,
            norm=norm,
            norm_kwargs=norm_kwargs,
            jk=jk,
        )
