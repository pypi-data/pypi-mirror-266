import os
from collections.abc import Iterable
from datetime import datetime
from typing import List, Union, Callable, Tuple, Dict

import h3
import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Data
from aq_utilities.engine.psql import get_engine
from aq_utilities.data import apply_filters, filter_aqsids, round_station_lat_lon, filter_lat_lon, remove_duplicate_aqsid, remove_duplicate_lat_lon
from aq_utilities.data import measurements_to_aqsid, determine_leaf_h3_resolution

from aq_geometric.data.remote import load_node_feature, load_node_features, load_nodes_info
from aq_geometric.data.file.local import load_hourly_data_from_fp, load_stations_info_from_fp, load_hourly_feature_from_fp, load_hourly_features_from_fp
from aq_geometric.data.graph.edges.compute_edges import get_edges_from_df
from aq_geometric.data.graph.nodes.compute_nodes import get_nodes_from_df
from aq_geometric.data.graph.nodes.compute_node_features import data_to_feature, get_node_feature, get_node_features, stack_node_features
from aq_geometric.data.graph.compute_graph import make_graph


class GraphsBuilder(Iterable):
    def __init__(
            self, features: List[str], targets: List[str], start_time: str,
            end_time: str, freq: str, time_closed_interval: bool = False,
            engine: Union["sqlalchemy.engine.Engine",
                          None] = None, stations_info_fp: Union[str,
                                                                None] = None,
            features_hourly_features_fps: Union[Dict[str, str], None] = None,
            targets_hourly_features_fps: Union[Dict[str, str], None] = None,
            selected_aqsids: Union[List[str], None] = None,
            selected_h3_indices: Union[List[str], None] = None,
            stations_info_filters: List[Callable] = [
                filter_aqsids,
                round_station_lat_lon,
                filter_lat_lon,
                remove_duplicate_aqsid,
                remove_duplicate_lat_lon,
            ], min_h3_resolution: int = 0,
            leaf_h3_resolution: Union[int, None] = None,
            max_h3_resolution: int = 12, include_root_node: bool = True,
            compute_edges: bool = True, make_undirected: bool = True,
            include_self_loops: bool = True, with_edge_features: bool = True,
            min_to_root_edge_distance: float = 0.0,
            node_missing_value: float = np.nan, verbose: bool = False):
        self.engine = engine
        self.stations_info_fp = stations_info_fp
        self.features_hourly_features_fps = features_hourly_features_fps
        self.targets_hourly_features_fps = targets_hourly_features_fps
        self.features = features
        self.targets = targets
        self.start_time = start_time
        self.end_time = end_time
        self.freq = freq
        self.time_closed_interval = time_closed_interval
        self.selected_aqsids = selected_aqsids
        self.stations_info_filters = stations_info_filters
        self.selected_h3_indices = selected_h3_indices
        self.min_h3_resolution = min_h3_resolution
        self.leaf_h3_resolution = leaf_h3_resolution
        self.max_h3_resolution = max_h3_resolution
        self.include_root_node = include_root_node
        self.compute_edges = compute_edges
        self.make_undirected = make_undirected
        self.include_self_loops = include_self_loops
        self.with_edge_features = with_edge_features
        self.min_to_root_edge_distance = min_to_root_edge_distance
        self.node_missing_value = node_missing_value
        self.verbose = verbose
        # compute the timestamps
        self.timestamps = _get_timestamps(
            start_time=self.start_time,
            end_time=self.end_time,
            freq=self.freq,
            time_closed_interval=self.time_closed_interval,
            verbose=self.verbose,
        )
        # compute the number of graphs
        self.num_graphs = _determine_num_graphs_from_timestamps(
            self.timestamps,
            verbose=self.verbose,
        )
        # we still need to load the data from the provided data source
        self._ready = False

    def from_engine(
        self,
        engine: "sqlalchemy.engine.Engine",
    ):
        self.engine = engine
        return self

    def from_engine_kwargs(
        self,
        engine_kwargs: dict,
    ):
        self.engine = get_engine(**engine_kwargs)
        return self

    def from_local_fps(
        self,
        nodes_info_fp: str,
        features_hourly_features_fps: Dict[str, str],
        targets_hourly_features_fps: Dict[str, str],
    ):
        self.stations_info_fp = nodes_info_fp
        self.features_hourly_features_fps = features_hourly_features_fps
        self.targets_hourly_features_fps = targets_hourly_features_fps
        return self

    def export_as_graph(self) -> Data:
        if not self._ready:
            self._load_data_from_source()
        assert self._ready, "data must be loaded from the source"

        graph_kwargs = {
            "nodes":
            self._nodes,
            "edges":
            self._edges[["from", "to"]].to_numpy().T,
            "edge_attr":
            self._edge_attr.drop(columns=["from", "to"]).to_numpy()
            if self.with_edge_features else None,
            "node_features":
            self._node_features,
            "targets":
            self._node_targets,
            "timestamps":
            self.timestamps,
            "feature_names":
            self.features,
            "target_names":
            self.targets,
            "node_missing_value":
            self.node_missing_value,
            "verbose":
            self.verbose,
        }
        # compute the graph
        graph = make_graph(**graph_kwargs)
        return graph

    def _check_data_source(self):
        if self.engine is None:
            if self.stations_info_fp is None:
                raise ValueError(
                    "either engine or stations_info_fp must be provided")
            assert os.path.exists(
                self.stations_info_fp
            ), f"file {self.stations_info_fp} does not exist"
            if self.features_hourly_features_fps is None:
                raise ValueError(
                    "features_hourly_features_fps must be provided")
            assert isinstance(
                self.features_hourly_features_fps,
                dict), "features_hourly_features_fps must be a dictionary"
            for k, v in self.features_hourly_features_fps.items():
                os.path.exists(v), f"file {v} for feature {k} does not exist"
            if self.targets_hourly_features_fps is None:
                raise ValueError(
                    "targets_hourly_features_fps must be provided")
            assert isinstance(
                self.targets_hourly_features_fps,
                dict), "targets_hourly_features_fps must be a dictionary"
            for k, v in self.targets_hourly_features_fps.items():
                os.path.exists(v), f"file {v} for target {k} does not exist"
        else:
            if self.stations_info_fp is not None:
                raise ValueError(
                    "stations_info_fp must be None if engine is provided")
            if self.features_hourly_features_fps is not None:
                raise ValueError(
                    "features_hourly_features_fps must be None if engine is provided"
                )
            if self.targets_hourly_features_fps is not None:
                raise ValueError(
                    "targets_hourly_features_fps must be None if engine is provided"
                )

    def _prepare_stations_info(self):
        if self.stations_info_fp is not None:
            # load the stations info from the local file
            stations_info_df = load_stations_info_from_fp(
                self.stations_info_fp)
        else:
            # load the stations info from the database
            stations_info_df = load_nodes_info(
                engine=self.engine,
                query_date=pd.to_datetime(self.start_time).date(
                ),  # get the date from the start time
                selected_aqsids=self.selected_aqsids,
                verbose=self.verbose,
            )
        if self.stations_info_filters is not None and len(
                self.stations_info_filters) > 0:
            stations_info_df = apply_filters(
                df=stations_info_df,
                filters=self.stations_info_filters,
                verbose=self.verbose,
            )
        if self.selected_aqsids is not None and len(self.selected_aqsids) > 0:
            stations_info_df = stations_info_df[stations_info_df["aqsid"].isin(
                self.selected_aqsids)]
        self._stations_info_df = stations_info_df

    def _load_data_from_source(self):
        self._check_data_source()
        self._prepare_stations_info()
        # compute nodes
        self._compute_nodes()
        # compute edges
        if self.compute_edges:
            self._compute_edges()
        # compute features
        self._compute_features()
        # compute targets
        self._compute_targets()
        # construct the generator
        self._ready = True
        self._gen = self._generate(self.num_graphs)

    def _compute_nodes(self):
        # determine the leaf h3 resolution if none is provided
        if self.leaf_h3_resolution is None:
            self.leaf_h3_resolution = determine_leaf_h3_resolution(
                df=self._stations_info_df,
                min_h3_resolution=self.min_h3_resolution,
                verbose=self.verbose,
            )
        # compute the nodes
        nodes = get_nodes_from_df(
            stations_info_df=self._stations_info_df,
            stations_info_filters=[],  # already applied
            selected_h3_indices=self.selected_h3_indices,
            min_h3_resolution=self.min_h3_resolution,
            leaf_h3_resolution=self.leaf_h3_resolution,
            max_h3_resolution=self.max_h3_resolution,
            include_root_node=self.include_root_node,
            verbose=self.verbose,
        )
        self._nodes = nodes

    def _compute_edges(self):
        # compute the edges
        edges = get_edges_from_df(
            stations_info_df=self._stations_info_df,
            selected_h3_indices=self.selected_h3_indices,
            min_h3_resolution=self.min_h3_resolution,
            leaf_h3_resolution=self.leaf_h3_resolution,
            with_edge_features=self.with_edge_features,
            include_root_node=self.include_root_node,
            make_undirected=self.make_undirected,
            include_self_loops=self.include_self_loops,
            min_to_root_edge_distance=self.min_to_root_edge_distance,
            verbose=self.verbose,
        )
        if self.with_edge_features:
            self._edges, self._edge_attr = edges
        else:
            self._edges = edges

    def _compute_features(self):
        # compute the node features
        node_features = []
        if self.features_hourly_features_fps is not None:
            # load the node features from the local file
            for feature in self.features:
                feature_fp = self.features_hourly_features_fps[feature]
                feature_df = load_hourly_feature_from_fp(feature_fp)
                feature = get_node_feature(
                    feature_df=feature_df,
                    timestamps=self.timestamps,
                    nodes=self._nodes,
                    verbose=self.verbose,
                )
                node_features.append(feature)
        else:
            # load the node features from the database
            for feature in self.features:
                data_df = load_node_feature(
                    engine=self.engine,
                    table="hourly_data",
                    start_time=self.start_time,
                    end_time=self.end_time,
                    feature=feature,
                    selected_aqsids=self.selected_aqsids,
                    verbose=self.verbose,
                )
                feature_df = data_to_feature(
                    df=data_df,
                    stations_info_df=self._stations_info_df,
                    min_h3_resolution=self.min_h3_resolution,
                    leaf_h3_resolution=self.leaf_h3_resolution,
                    verbose=self.verbose,
                )
                feature = get_node_feature(
                    feature_df=feature_df,
                    timestamps=self.timestamps,
                    nodes=self._nodes,
                    verbose=self.verbose,
                )
                node_features.append(feature)
        self._node_features = stack_node_features(self._nodes, node_features)

    def _compute_targets(self):
        # compute the targets
        node_targets = []
        if self.targets_hourly_features_fps is not None:
            # load the node features from the local file
            for feature in self.targets:
                feature_fp = self.targets_hourly_features_fps[feature]
                feature_df = load_hourly_feature_from_fp(feature_fp)
                feature = get_node_feature(
                    feature_df=feature_df,
                    timestamps=self.timestamps,
                    nodes=self._nodes,
                    verbose=self.verbose,
                )
                node_targets.append(feature)
        else:
            # load the node features from the database
            for feature in self.targets:
                data_df = load_node_feature(
                    engine=self.engine,
                    table="hourly_data",
                    start_time=self.start_time,
                    end_time=self.end_time,
                    feature=feature,
                    selected_aqsids=self.selected_aqsids,
                    verbose=self.verbose,
                )
                feature_df = data_to_feature(
                    df=data_df,
                    stations_info_df=self._stations_info_df,
                    min_h3_resolution=self.min_h3_resolution,
                    leaf_h3_resolution=self.leaf_h3_resolution,
                    verbose=self.verbose,
                )
                feature = get_node_feature(
                    feature_df=feature_df,
                    timestamps=self.timestamps,
                    nodes=self._nodes,
                    verbose=self.verbose,
                )
                node_targets.append(feature)
        self._node_targets = stack_node_features(self._nodes, node_targets)

    def __iter__(self):
        if not self._ready:
            self._load_data_from_source()
        assert self._ready, "data must be loaded from the source"

        return self

    def __next__(self) -> Data:
        return next(self._gen)

    def _generate(self, n):
        if not self._ready:
            self._load_data_from_source()
        assert self._ready, "data must be loaded from the source"

        for i in range(n):
            timestamp = self.timestamps[i]

            if self.verbose:
                print(
                    f"[{datetime.now()}] generating graph {i + 1}/{n} at timestamp {timestamp}"
                )

            node_features = self._node_features[:, i, :]
            targets = self._targets[:, i, :]
            graph = make_graph(
                nodes=self._nodes,
                edges=self._edges,
                node_features=node_features,
                targets=targets,
                timestamps=np.array([timestamp]),
                feature_names=self.features,
                target_names=self.targets,
                node_missing_value=self.node_missing_value,
                verbose=self.verbose,
            )
            yield graph


def _get_timestamps(
    start_time: str,
    end_time: str,
    freq: str,
    time_closed_interval: bool,
    verbose: bool = False,
) -> pd.DatetimeIndex:
    """Get the timestamps."""
    if verbose:
        print(f"[{datetime.now()}] getting the timestamps")
    # get the timestamps
    timestamps = pd.date_range(
        start=start_time,
        end=end_time,
        freq=freq,
        inclusive="both" if time_closed_interval == True else "left",
    )
    if verbose:
        print(f"[{datetime.now()}] got {len(timestamps)} timestamps")
        print(f"[{datetime.now()}] first timestamp is {timestamps[0]}")
        print(f"[{datetime.now()}] last timestamp is {timestamps[-1]}")
    return timestamps


def _determine_num_graphs_from_timestamps(
    timestamps: pd.DatetimeIndex,
    verbose: bool = False,
) -> int:
    """Determine the number of graphs from the timestamps."""
    if verbose:
        print(
            f"[{datetime.now()}] determining the number of graphs from the timestamps"
        )
    num_graphs = len(timestamps)
    if verbose:
        print(
            f"[{datetime.now()}] determined {num_graphs} graphs from the timestamps"
        )

    return num_graphs
