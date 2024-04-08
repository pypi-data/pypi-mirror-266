from typing import List, Union

import uuid
import torch
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Linear, ReLU
from torch_geometric.nn import MessagePassing

from aq_geometric.models.base_model import BaseModel


class EdgeConv(MessagePassing):
    r"""EdgeConv layer for predicting air quality.
    
    This basic EdgeConv implementation is based on the following paper:
    https://arxiv.org/abs/1801.07829
    """
    def __init__(self, in_channels: int, out_channels: int, aggr: str = "max"):
        super().__init__(aggr=aggr)
        self.mlp = Seq(Linear(2 * in_channels, out_channels), ReLU(),
                       Linear(out_channels, out_channels))

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor):
        # x has shape [N, in_channels]
        # edge_index has shape [2, E]

        return self.propagate(edge_index, x=x)

    def message(self, x_i: torch.Tensor, x_j: torch.Tensor):
        # x_i has shape [E, in_channels]
        # x_j has shape [E, in_channels]

        tmp = torch.cat([x_i, x_j - x_i],
                        dim=1)  # tmp has shape [E, 2 * in_channels]
        return self.mlp(tmp)


class EdgeConvModel(BaseModel):
    r"""EdgeConv model for predicting air quality.
    
    This basic EdgeConv implementation is based on the following paper:
    https://arxiv.org/abs/1801.07829
    
    Args:
        name (str): The name of the model.
        guid (str): The unique identifier for the model.
        stations (list): The list of stations to use for the model.
        in_channels (int): The number of input channels.
        out_channels (int): The number of output channels.
        linear_hidden (int): The number of hidden units for the linear layer.
        linear_out (int): The number of output units for the linear layer.    
    """
    def __init__(
        self,
        name: str = "EdgeConvModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        in_channels: int = 48,
        out_channels: int = 256,
        aggr: str = "max",
        linear_hidden: int = 16,
        linear_out: int = 1,
    ):
        super().__init__(name=name, guid=guid, stations=stations)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.conv1 = EdgeConv(in_channels, out_channels, aggr)
        self.conv2 = EdgeConv(out_channels, out_channels, aggr)
        self.conv3 = EdgeConv(out_channels, out_channels, aggr)
        self.max_pool = torch.nn.MaxPool1d(in_channels)
        self.fc = torch.nn.Linear(
            linear_hidden, linear_out
        )  # shape of the input to the linear layer is 8 for 128 hidden units and 16 for 256?

    def forward(self, x, edge_index):
        """Define the forward pass for the EdgeConv model."""
        # forward pass through the edge convolutions
        x_1 = self.conv1(x, edge_index)
        x_2 = x_1.relu()
        x_3 = self.conv2(x_2, edge_index)
        x_4 = x_3.relu()
        x_5 = self.conv3(x_4, edge_index)
        x_6 = x_5.relu()

        # concatenate
        x_7 = torch.cat((x_2, x_4, x_6), dim=1)

        # max pool
        x_8 = self.max_pool(x_7)

        # linear
        x_9 = self.fc(x_8)

        return x_9


class AqEdgeConvModel(BaseModel):
    r"""EdgeConv model for predicting air quality.
    
    This basic EdgeConv implementation is based on the following paper:
    https://arxiv.org/abs/1801.07829
    
    Args:
        name (str): The name of the model.
        guid (str): The unique identifier for the model.
        stations (list): The list of stations to use for the model.
        in_channels (int): The number of input channels.
        out_channels (int): The number of output channels.
        linear_hidden (int): The number of hidden units for the linear layer.
        linear_out (int): The number of output units for the linear layer.    
    """
    def __init__(
        self,
        name: str = "AqEdgeConvModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        features: List[str] = ["OZONE", "PM2.5", "NO2"],
        targets: List[str] = ["OZONE", "PM2.5", "NO2"],
        num_samples_in_node_feature: int = 48,
        num_samples_in_node_target: int = 12,
        num_features_in_node_feature: int = 3,
        num_features_in_node_target: int = 3,
        conv_out_channels: int = 256,
        aggr: str = "max",
        verbose: bool = False,
    ):
        super().__init__(name=name, guid=guid, stations=stations)
        self.features = features
        self.targets = targets
        self.verbose = verbose
        self.num_samples_in_node_feature = num_samples_in_node_feature
        self.num_samples_in_node_target = num_samples_in_node_target
        self.num_features_in_node_feature = num_features_in_node_feature
        self.num_features_in_node_target = num_features_in_node_target
        
        self.hidden_channels = num_samples_in_node_feature * num_features_in_node_feature
        self.out_channels = num_samples_in_node_target * num_features_in_node_target
        
        self.in_norm = torch.nn.LayerNorm(self.hidden_channels)  # layer norm
        self.in_mlp = Seq(Linear(self.hidden_channels, self.hidden_channels),
                          ReLU(),
                          Linear(self.hidden_channels, self.hidden_channels))
        
        self.conv1 = EdgeConv(self.hidden_channels, conv_out_channels, aggr)
        self.max_pool = torch.nn.MaxPool1d(self.hidden_channels)

        self.out_mlp = Seq(Linear((conv_out_channels+2), self.out_channels),
                          ReLU(),
                          Linear(self.out_channels, self.out_channels))

    def forward(self, x, edge_index):
        """Define the forward pass for the EdgeConv model."""
        # x has shape [N, in_channels, in_features]
        # return x has shape [N, out_channels, out_features]
        x = torch.reshape(x, (-1, self.hidden_channels))
        # apply layer norm
        x = self.in_norm(x)
        # apply mlp
        x = self.in_mlp(x)
        # forward pass through the edge convolutions
        x = self.conv1(x, edge_index)
        # max pool
        x_pooled = self.max_pool(x)
        # linear
        x = self.out_mlp(torch.cat((x, x_pooled), dim=1))

        return x
