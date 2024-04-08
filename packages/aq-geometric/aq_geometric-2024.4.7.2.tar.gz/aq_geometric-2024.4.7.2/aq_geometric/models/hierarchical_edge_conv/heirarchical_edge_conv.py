import os
from typing import Dict, List, Tuple, Union

import uuid
import torch
import h3
import numpy as np
from torch.nn import Sequential as Seq, Linear, ReLU
from torch_geometric.nn import MessagePassing, ChebConv
from torch_geometric.nn import aggr

from aq_geometric.models.base_model import BaseModel


class HierarchicalEdgeConv(MessagePassing):
    def __init__(self, in_channels, aggr=aggr.SoftmaxAggregation(learn=True)):
        super().__init__(aggr=aggr)
        self.mlp = Seq(Linear(2 * in_channels, in_channels), ReLU(),
                       Linear(in_channels, in_channels))

    def forward(self, x, edge_index):
        # x has shape [N, in_channels]
        # edge_index has shape [2, E]

        return self.propagate(edge_index, x=x)

    def message(self, x_i, x_j):
        # x_i has shape [E, in_channels]
        # x_j has shape [E, in_channels]

        tmp = torch.cat([x_i, x_j - x_i],
                        dim=1)  # tmp has shape [E, 2 * in_channels]
        return self.mlp(tmp)


class ChebGraphConv(MessagePassing):
    def __init__(self, in_channels, out_channels, K=2):
        super().__init__(aggr='add')
        self.lin = Linear(in_channels, out_channels)
        self.conv = ChebConv(in_channels, out_channels, K=K)

    def forward(self, x, edge_index):
        return self.propagate(edge_index, x=x)


class AqHierarchicalEdgeConvModel(BaseModel):
    r"""A hierarchical edge convolution model for predicting air quality.
    
    Args:
        edges_low_to_high_resolution (Dict[int, torch.Tensor]): the edges from low to high resolution
        edges_high_to_low_resolution (Dict[int, torch.Tensor]): the edges from high to low resolution
        name (str): the name of the model
        guid (str): the guid of the model
        stations (Union[List, None]): the stations
        features (List[str]): the features
        targets (List[str]): the targets
        num_samples_in_node_feature (int): the number of samples in the node feature
        num_samples_in_node_target (int): the number of samples in the node target
        num_features_in_node_feature (int): the number of features in the node feature
        num_features_in_node_target (int): the number of features in the node target
        finest_resolution (int): the finest resolution
        coarsest_resolution (int): the coarsest resolution
        cheb_k (int): the number of chebyshev polynomials
        verbose (bool): whether to print out information about the model
    """
    def __init__(
        self,
        edges_low_to_high_resolution: Dict[int, torch.Tensor] = None,
        edges_high_to_low_resolution: Dict[int, torch.Tensor] = None,
        name: str = "AqHierarchicalEdgeConvModel",
        guid: str = str(uuid.uuid4()),
        stations: Union[List, None] = None,
        features: List[str] = ["OZONE", "PM2.5", "NO2"],
        targets: List[str] = ["OZONE", "PM2.5", "NO2"],
        num_samples_in_node_feature: int = 48,
        num_samples_in_node_target: int = 12,
        finest_resolution: int = 6,
        coarsest_resolution: int = -1,
        cheb_k: int = 2,
        verbose: bool = False,
    ):
        super().__init__(name=name, guid=guid, stations=stations, features=features, targets=targets, num_samples_in_node_feature=num_samples_in_node_feature, num_samples_in_node_target=num_samples_in_node_target)
        self.num_features_in_node_feature = len(features)
        self.num_features_in_node_target = len(targets)
        self.finest_resolution = finest_resolution
        self.coarsest_resolution = coarsest_resolution
        self.cheb_k = cheb_k
        self.num_resolutions_between_finest_and_coarsest = finest_resolution - coarsest_resolution
        self.edges_low_to_high_resolution = edges_low_to_high_resolution
        self.edges_high_to_low_resolution = edges_high_to_low_resolution
        self.verbose = verbose
       
        self.hidden_channels = self.num_samples_in_node_feature * self.num_features_in_node_feature
        self.in_norm = torch.nn.LayerNorm(self.hidden_channels)  # layer norm
        self.in_mlp = Seq(Linear(self.hidden_channels, self.hidden_channels),
                          ReLU(),
                          Linear(self.hidden_channels, self.hidden_channels))
        self.max_pool = torch.nn.MaxPool1d(self.hidden_channels)  # max pool
        self.learned_pool = Linear(
            self.hidden_channels + 3, self.hidden_channels
        )  # learned pool for the 4 pooled or convolved features
        self.out_channels = self.num_samples_in_node_target * self.num_features_in_node_target
        self.out_mlp = Seq(Linear(self.hidden_channels, self.out_channels))
        self.edge_conv = HierarchicalEdgeConv(self.hidden_channels)
        self.node_target_conv = ChebGraphConv(self.hidden_channels,
                                              self.hidden_channels,
                                              K=self.cheb_k)
        self.node_target_mlp = Seq(
            Linear(self.hidden_channels, self.hidden_channels), ReLU(),
            Linear(self.hidden_channels, self.hidden_channels))

    def forward(self, x, edge_index):
        # x has shape [N, in_channels, in_features]
        # return x has shape [N, out_channels, out_features]
        x = torch.reshape(x, (-1, self.hidden_channels))
        # apply layer norm
        xn = self.in_norm(x)
        # apply in mlp
        xs = self.in_mlp(xn)
        # apply max pool
        xp1 = self.max_pool(xs)
        # apply edge conv at each level of resolution
        fine_res = self.finest_resolution
        coarse_res = fine_res - 1
        for _ in range(self.num_resolutions_between_finest_and_coarsest
                       ):  # @TODO update
            # apply edge conv from high to low resolution
            xs = self.edge_conv(
                xs, self.edges_high_to_low_resolution[fine_res].to(x.device))
            fine_res -= 1
            coarse_res -= 1
        # apply max pool
        xp2 = self.max_pool(xs)
        # apply edge conv at each level of resolution
        for _ in range(self.num_resolutions_between_finest_and_coarsest):
            # apply edge conv from low to high resolution
            xs = self.edge_conv(
                xs, self.edges_low_to_high_resolution[fine_res].to(x.device))
            coarse_res += 1
            fine_res += 1
        # apply max pool
        xp3 = self.max_pool(xs)
        # concatenate the pooled and the edge convolved features
        x = torch.cat((xs, xp1, xp2, xp3), dim=1)
        # apply a learned pooling
        x = self.learned_pool(x)
        # apply cheb graph conv
        x = self.node_target_conv(x, edge_index)
        # apply node target mlp
        x = self.node_target_mlp(x)
        # apply out mlp
        x = self.out_mlp(x)

        return x

    def save(self, path: str):
        """Save the model to a file."""
        # ensure the model is on the CPU
        self.cpu()

        # ensure the path exists
        # check if the path has a directory
        if os.path.dirname(path):
            # create the directory if it does not exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

        # gather the model data
        model_data = {
            "name": self.name,
            "guid": self.guid,
            "stations": self.stations,
            "edges_high_to_low_resolution": self.edges_high_to_low_resolution,
            "edges_low_to_high_resolution": self.edges_low_to_high_resolution,
            "features": self.features,
            "targets": self.targets,
            "num_samples_in_node_feature": self.num_samples_in_node_feature,
            "num_samples_in_node_target": self.num_samples_in_node_target,
            "finest_resolution": self.finest_resolution,
            "coarsest_resolution": self.coarsest_resolution,
            "cheb_k": self.cheb_k,
            "state_dict": self.state_dict(),
            **self.kwargs
        }
        # save the model data
        torch.save(model_data, path)

    def load(self, path: str):
        """Load the model from a file."""
        # load the model data
        model_data = torch.load(path)

        # set the model data
        self.name = model_data["name"]
        self.guid = model_data["guid"]
        self.stations = model_data["stations"]
        self.edges_high_to_low_resolution = model_data[
            "edges_high_to_low_resolution"]
        self.edges_low_to_high_resolution = model_data[
            "edges_low_to_high_resolution"]
        self.features = model_data["features"]
        self.targets = model_data["targets"]
        self.num_samples_in_node_feature = model_data[
            "num_samples_in_node_feature"]
        self.num_samples_in_node_target = model_data[
            "num_samples_in_node_target"]
        self.finest_resolution = model_data.get("finest_resolution")
        self.coarsest_resolution = model_data.get("coarsest_resolution")
        self.cheb_k = model_data.get("cheb_k")

        self.load_state_dict(model_data["state_dict"])

        # set the kwargs
        for key, value in model_data.items():
            if key not in ["name", "guid", "stations", "edges_high_to_low_resolution", "edges_low_to_high_resolution", "features", "targets", "num_samples_in_node_feature", "num_samples_in_node_target", "num_features_in_node_feature", "num_features_in_node_target", "state_dict"]:
                setattr(self, key, value)

    def __repr__(self):
        """Use the torch default representation, add new attrs."""
        representation = super().__repr__()
        # add new lines with the name, guid, and stations
        representation += f"\nFinest h3 resolution: {self.finest_resolution}"
        representation += f"\Coarsest h3 resolution: {self.coarsest_resolution}"

        return representation


def process_aq_geometric_dataset_edges_by_h3_resolution(
    graph: "torch_geometric.data.data.Data",
    graph_includes_root_node: bool = True,
    force_self_loops: bool = True,
    force_bidirectional_edges: bool = True,
    verbose: bool = False,
) -> Tuple["torch_geometric.data.data.Data", torch.Tensor]:
    """Process a graph from the AQ Geometric Dataset to be used in a PyTorch model.
    
    The graph is processed to handle missing values and has its edge_index data
    modified in place based on provided conditions. We can specify the following:
    - missing_value: the value to use for missing data.
    - graph_includes_root_node: whether the graph includes a root node.
    - force_self_loops: whether to force self loops in the graph.
    - force_bidirectional_edges: whether to force bidirectional edges in the graph.
    - verbose: whether to print out information about the processing.

    Args:
    - graph: a graph from the AQ Geometric Dataset.
    - graph_includes_root_node: whether the graph includes a root node.
    - force_self_loops: whether to force self loops in the graph.
    - force_bidirectional_edges: whether to force bidirectional edges in the graph.
    - verbose: whether to print out information about the processing.

    Returns:
    - graph: processed graph [x, edge_index, ..., y]
    - edge_index_by_source_node_h3_resolution: edge indices at each h3 resolution.
    """
    # validate the graph
    assert graph.x.shape[0] == graph.h3_index.shape[0]

    # obtain the h3_index from the graph
    h3_index = graph.h3_index
    # determine the highest h3 resolution
    max_h3_resolution = int(
        np.max([h3.h3_get_resolution(h) for h in h3_index if h != "root"]))
    # set the coarsest h3 resolution
    if graph_includes_root_node:
        min_h3_resolution = -1
    else:
        min_h3_resolution = 0

    # obtain the node_to_h3_resolution_map
    if graph_includes_root_node:
        node_to_h3_resolution_map = {
            i: h3.h3_get_resolution(h3_index[i])
            for i in range(h3_index.shape[0] - 1)
        }  # the last node is the root node
        node_to_h3_resolution_map[graph.num_nodes - 1] = -1  # the root node
    else:
        node_to_h3_resolution_map = {
            i: h3.h3_get_resolution(h3_index[i])
            for i in range(h3_index.shape[0])
        }

    # for each resolution between these two, obtain the edge_index
    # we need to track edges based on if they are within the same resolution, or if they are between resolutions
    edges_same_resolution = {
        **{
            _: []
            for _ in range(min_h3_resolution, max_h3_resolution + 1)
        }
    }
    edges_high_to_low_resolution = {
        **{
            _: []
            for _ in range(min_h3_resolution, max_h3_resolution + 1)
        }
    }
    edges_low_to_high_resolution = {
        **{
            _: []
            for _ in range(min_h3_resolution, max_h3_resolution + 1)
        }
    }

    # get the self edges if needed
    self_edges = None
    if force_self_loops:
        self_edges = torch.stack([
            torch.arange(0, graph.num_nodes, dtype=int),
            torch.arange(0, graph.num_nodes, dtype=int)
        ], dim=0)

    # iterate over the edges in the graph
    for _, e in enumerate(graph.edge_index.T):
        from_, to = int(e[0]), int(e[1])  # COO format node ids
        from_h3_resolution = node_to_h3_resolution_map[from_]
        to_h3_resolution = node_to_h3_resolution_map[to]
        # determine which type of edge this is
        if from_h3_resolution == to_h3_resolution:
            edges_same_resolution[from_h3_resolution].append([from_, to])
        elif from_h3_resolution > to_h3_resolution:
            edges_high_to_low_resolution[from_h3_resolution].append(
                [from_, to])
            if force_bidirectional_edges:
                edges_low_to_high_resolution[to_h3_resolution].append(
                    [to, from_])

    for k in range(min_h3_resolution, max_h3_resolution + 1):
        if verbose:
            print(f"processing edges and edge attributes at h3 resolution {k}")
        edges_same_resolution[k] = torch.cat(
            (self_edges, torch.tensor(edges_same_resolution[k], dtype=int).T),
            dim=1)
        edges_high_to_low_resolution[k] = torch.cat(
            (edges_same_resolution[k],
             torch.tensor(edges_high_to_low_resolution[k], dtype=int).T),
            dim=1)
        edges_low_to_high_resolution[k] = torch.cat(
            (edges_same_resolution[k],
             torch.tensor(edges_low_to_high_resolution[k], dtype=int).T),
            dim=1)
        if verbose:
            print(
                f"before removing duplicates, edges have shape: {edges_same_resolution[k].shape}, {edges_high_to_low_resolution[k].shape}, {edges_low_to_high_resolution[k].shape}"
            )
        edges_same_resolution[k] = torch.unique(edges_same_resolution[k],
                                                dim=1)
        edges_high_to_low_resolution[k] = torch.unique(
            edges_high_to_low_resolution[k], dim=1)
        edges_low_to_high_resolution[k] = torch.unique(
            edges_low_to_high_resolution[k], dim=1)
        if verbose:
            print(
                f"after removing duplicates, edges have shapes:\n  -> same resolution: {edges_same_resolution[k].shape}\n  -> high to low resolution: {edges_high_to_low_resolution[k].shape}\n  -> low to high resolution: {edges_low_to_high_resolution[k].shape}"
            )

    # change the graph's edge_index in place
    if verbose: print("changing the graph's edge_index in place")
    new_edge_index = torch.unique(
        torch.cat([
            torch.cat(
                (edges_same_resolution[k], edges_low_to_high_resolution[k],
                 edges_high_to_low_resolution[k]), dim=1)
            for k in range(min_h3_resolution, max_h3_resolution + 1)
        ], dim=1), dim=1)
    if verbose:
        print(
            f"old edge_index shape: {graph.edge_index.shape}, new edge_index shape: {new_edge_index.shape}"
        )
    graph.edge_index = new_edge_index

    return graph, edges_same_resolution, edges_high_to_low_resolution, edges_low_to_high_resolution
