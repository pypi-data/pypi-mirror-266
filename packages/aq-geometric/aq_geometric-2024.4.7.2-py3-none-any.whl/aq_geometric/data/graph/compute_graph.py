from datetime import datetime
from typing import List, Union

import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Data


def make_graph(
    nodes: np.ndarray,
    edges: Union[np.ndarray, None],
    edge_attr: Union[np.ndarray, None],
    node_features: np.ndarray,
    targets: np.ndarray,
    timestamps: Union[np.ndarray, pd.DatetimeIndex],
    feature_names: List[str],
    target_names: List[str],
    node_missing_value: Union[int, float] = np.nan,
    verbose: bool = False,
) -> Data:
    """Make a graph from the nodes and edges."""

    if isinstance(timestamps, pd.DatetimeIndex):
        timestamps = timestamps.to_numpy()
    if isinstance(nodes, pd.DataFrame):
        nodes = nodes[["h3_index", "aqsid", "node_id"
                       ]].to_numpy()  # this should already be a numpy array

    assert nodes.shape[0] == node_features.shape[
        0], "nodes and node_features must have the same number of rows"
    assert nodes.shape[0] == targets.shape[
        0], "nodes and targets must have the same number of rows"
    assert node_features.shape[1] == len(
        timestamps
    ), "node_features must have the same number of columns as timestamps"
    assert targets.shape[1] == len(
        timestamps
    ), "targets must have the same number of columns as timestamps"
    assert len(feature_names) == node_features.shape[
        2], "feature_names must have the same number of elements as node_features columns"
    assert len(target_names) == targets.shape[
        2], "target_names must have the same number of elements as targets columns"
    if edges is not None:
        assert edges.shape[0] == 2, "edges must have shape (2, num_edges)"
    if edge_attr is not None:
        assert edge_attr.shape[0] == edges.shape[
            1], "edge_attr must have the same number of rows as edge_index columns"
        assert isinstance(edge_attr,
                          np.ndarray), "edge_attr must be a numpy array"

    if verbose:
        print(
            f"[{datetime.now()}] making graph from nodes of shape {nodes.shape} with features of shape {node_features.shape} and targets of shape {targets.shape}"
        )

    # we need to map from edges to edge_index
    h3_index_to_id_map = {v[0]: v[2] for v in nodes}

    # we need to map the edges from h3 index to node id
    if edges is not None:
        edge_index = np.array([
            (h3_index_to_id_map[e[0]], h3_index_to_id_map[e[1]])
            for e in edges.T
            if e[0] in h3_index_to_id_map and e[1] in h3_index_to_id_map
        ]).T
    else:
        edge_index = None
    # the same applies for the edge_attr if provided

    # we need to handle missing values (negative 1 or np.nan) with a mask
    x_mask = torch.tensor(
        node_features >= 0, dtype=torch.bool
    )  # some stations report negative values which are nonphysical
    y_mask = torch.tensor(targets >= 0, dtype=torch.bool)
    # combine the masks for an overall missingness mask
    node_features_mask = torch.all(torch.all(x_mask, dim=1), dim=1)
    node_targets_mask = torch.all(torch.all(y_mask, dim=1), dim=1)
    node_all_valid_measurements_mask = torch.all(
        torch.stack((node_features_mask, node_targets_mask), dim=1), dim=1)

    # we need to handle missing values
    node_features = np.nan_to_num(node_features, nan=node_missing_value)
    targets = np.nan_to_num(targets, nan=node_missing_value)

    if verbose:
        print(f"[{datetime.now()}] x_mask has shape {x_mask.shape}")
    if verbose:
        print(f"[{datetime.now()}] y_mask has shape {y_mask.shape}")
    if verbose:
        print(
            f"[{datetime.now()}] node_all_valid_measurements_mask has shape {node_all_valid_measurements_mask.shape}"
        )

    edge_node_all_valid_measurements_mask = torch.logical_and(
        node_all_valid_measurements_mask[edge_index[0]],
        node_all_valid_measurements_mask[edge_index[1]])

    if verbose:
        print(
            f"[{datetime.now()}] edge_node_all_valid_measurements_mask has shape {edge_node_all_valid_measurements_mask.shape}"
        )

    if verbose: print(f"[{datetime.now()}] processed masks")

    # make the graph
    graph = Data(
        x=torch.tensor(node_features, dtype=torch.float),
        edge_index=torch.tensor(edge_index, dtype=torch.long),
        edge_attr=torch.tensor(edge_attr, dtype=torch.float)
        if edge_attr is not None else None,
        y=torch.tensor(targets, dtype=torch.float),
        h3_index=nodes.T[0],
        aqsid=nodes.T[1],
        timestamps=timestamps,
        feature_timestamps=timestamps,
        target_timestamps=timestamps,
        node_all_valid_measurements_mask=node_all_valid_measurements_mask,
        edge_node_all_valid_measurements_mask=
        edge_node_all_valid_measurements_mask,
        x_mask=x_mask,
        y_mask=y_mask,
        node_features_mask=node_features_mask,
        node_targets_mask=node_targets_mask,
        feature_start_time=timestamps[0],
        feature_end_time=timestamps[-1],
        target_start_time=timestamps[0],
        target_end_time=timestamps[-1],
    )
    graph.validate()

    return graph
