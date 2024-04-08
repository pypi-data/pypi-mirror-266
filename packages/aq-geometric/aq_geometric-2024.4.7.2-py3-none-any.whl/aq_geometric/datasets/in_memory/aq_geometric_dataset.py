from datetime import datetime
from typing import List, Union, Callable, Dict

import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Data, InMemoryDataset
from aq_utilities.engine.psql import get_engine
from aq_utilities.data import filter_aqsids, round_station_lat_lon, filter_lat_lon, remove_duplicate_aqsid, remove_duplicate_lat_lon

from aq_geometric.data.graph.graphs_builder import GraphsBuilder


class AqGeometricInMemoryDataset(InMemoryDataset):
    def __init__(
            self, root, transform: Union[Callable, None] = None,
            pre_transform: Union[Callable,
                                 None] = None, pre_filter: Union[Callable,
                                                                 None] = None,
            features: List[str] = ["PM2.5"], targets: List[str] = [
                "OZONE"
            ], start_time: str = "2023-01-01", end_time: str = "2023-01-15",
            freq: str = "1H", samples_in_node_features: int = 24,
            samples_in_node_targets: int = 24,
            time_closed_interval: bool = False,
            engine: Union["sqlalchemy.engine.Engine", None] = None,
            engine_kwargs: Dict = {}, selected_aqsids: Union[List[str],
                                                             None] = None,
            selected_h3_indices: Union[List[str], None] = None,
            stations_info_filters: List[Callable] = [
                filter_aqsids,
                round_station_lat_lon,
                filter_lat_lon,
                remove_duplicate_aqsid,
                remove_duplicate_lat_lon,
            ], min_h3_resolution: int = 0, leaf_h3_resolution: Union[int,
                                                                     None] = 6,
            max_h3_resolution: int = 12, include_root_node: bool = True,
            compute_edges: bool = True, make_undirected: bool = True,
            include_self_loops: bool = True, with_edge_features: bool = True,
            min_to_root_edge_distance: float = 0.0,
            node_missing_value: float = np.nan, verbose: bool = False):
        self.engine = engine if engine is not None else get_engine(
            **engine_kwargs)
        self.features = features
        self.targets = targets
        self.start_time = start_time
        self.end_time = end_time
        self.freq = freq
        self.time_closed_interval = time_closed_interval
        self.num_samples_in_node_features = samples_in_node_features
        self.num_samples_in_node_targets = samples_in_node_targets
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

        # prepare graph data in memory
        self._graph_data = GraphsBuilder(
            engine=self.engine, features=self.features, targets=self.targets,
            start_time=self.start_time, end_time=self.end_time, freq=self.freq,
            time_closed_interval=self.time_closed_interval,
            selected_aqsids=self.selected_aqsids,
            stations_info_filters=self.stations_info_filters,
            selected_h3_indices=self.selected_h3_indices,
            min_h3_resolution=self.min_h3_resolution,
            leaf_h3_resolution=self.leaf_h3_resolution,
            max_h3_resolution=self.max_h3_resolution,
            include_root_node=self.include_root_node,
            compute_edges=self.compute_edges,
            make_undirected=self.make_undirected,
            include_self_loops=self.include_self_loops,
            with_edge_features=self.with_edge_features,
            min_to_root_edge_distance=self.min_to_root_edge_distance,
            node_missing_value=self.node_missing_value,
            verbose=self.verbose).export_as_graph()

        # obtain the timestamps for the features and targets
        self.timestamps = self._graph_data.timestamps
        # determine the start and end times and index ranges for the graph
        self.graph_feature_start_timestamps = self.timestamps[
            0:-self.num_samples_in_node_targets]
        self.graph_target_start_timestamps = self.timestamps[
            self.num_samples_in_node_features:]

        # save the length as the number of time steps minus the number of samples in the node feature minus the number of samples in the node target
        self.num_graphs = 1 + len(
            self.timestamps
        ) - self.num_samples_in_node_features - self.num_samples_in_node_targets

        super().__init__(root, transform, pre_transform, pre_filter)

        # override the __getitem__ method
        self.__getitem__ = self.__indexed_getitem__

    @property
    def raw_file_names(self) -> list:
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return []

    @property
    def processed_file_names(self) -> list:
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return []

    def clear(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return None

    def download(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return None

    def process(self):
        """The InMemoryDataset class requires this property to be implemented, but it is not used in this class."""
        return None

    def len(self):
        return self.num_graphs

    def get(self, idx):
        """Obtain a graph from the dataset."""
        # ensure we have the graph index ranges
        assert idx < self.num_graphs, f"Index {idx} is out of range for the number of graphs {self.num_graphs}."

        if self.verbose:
            print(
                f"[{datetime.now()}] Getting graph {idx} of {self.num_graphs}")
        return self.__indexed_getitem__(idx)

    def __indexed_getitem__(self, idx):
        """Compute the graph for index idx using data from disk."""
        # determine which graph on disk has index idx
        time_index_start = idx
        time_index_end = idx + self.num_samples_in_node_features + self.num_samples_in_node_targets

        data = self._load_data_from_memory(time_index_start, time_index_end)

        if self.transform is not None:
            data = self.transform(data)

        return data

    def _load_data_from_memory(
        self,
        time_index_start: int,
        time_index_end: int,
    ) -> Data:
        """Load some or all of the graph from memory."""
        # we static edge_index and edge_attr
        edge_index = self._graph_data.edge_index
        edge_attr = self._graph_data.edge_attr

        # we need to compute the feature and target start and end times
        feature_start_time = pd.to_datetime(
            self._graph_data.feature_start_time) + (pd.Timedelta(self.freq) *
                                                    (time_index_start))
        feature_timestamps = pd.date_range(
            start=feature_start_time,
            periods=self.num_samples_in_node_features, freq=self.freq)
        feature_end_time = feature_timestamps[-1]

        target_start_time = feature_end_time + pd.Timedelta(self.freq)
        target_timestamps = pd.date_range(
            target_start_time, periods=self.num_samples_in_node_targets,
            freq=self.freq)
        target_end_time = target_timestamps[-1]

        # cast to numpy
        feature_timestamps = feature_timestamps.to_numpy()
        target_timestamps = target_timestamps.to_numpy()

        if self.verbose:
            print(f"feature_start_time: {feature_start_time}")
            print(f"feature_end_time: {feature_end_time}")
            print(f"target_start_time: {target_start_time}")
            print(f"target_end_time: {target_end_time}")
            print(f"time index start: {time_index_start}")
            print(f"time index end: {time_index_end}")

        start_idx, end_idx = time_index_start, time_index_end
        node_features = self._graph_data.x[:, start_idx:start_idx + self.
                                           num_samples_in_node_features].numpy(
                                           )
        node_targets = self._graph_data.y[:, start_idx +
                                          self.num_samples_in_node_features:
                                          end_idx].numpy()
        # handle missing values
        node_features = np.nan_to_num(node_features,
                                      nan=self.node_missing_value)
        node_targets = np.nan_to_num(node_targets, nan=self.node_missing_value)

        # get the node mapping attributes from the current graph
        h3_index = self._graph_data.h3_index
        aqsid = self._graph_data.aqsid

        x_mask = self._graph_data.x_mask[:, start_idx:start_idx +
                                         self.num_samples_in_node_features]
        y_mask = self._graph_data.y_mask[:, start_idx + self.
                                         num_samples_in_node_features:end_idx]

        if self.verbose:
            # print shapes
            print(f"node_features shape: {node_features.shape}")
            print(f"node_targets shape: {node_targets.shape}")
            print(f"x_mask shape: {x_mask.shape}")
            print(f"y_mask shape: {y_mask.shape}")
            print(f"edge_index shape: {edge_index.shape}")
            print(f"edge_attr shape: {edge_attr.shape}")

        # we need to compute the rest of the masks
        node_features_mask = torch.all(torch.all(x_mask, dim=1), dim=1)
        node_targets_mask = torch.all(torch.all(y_mask, dim=1), dim=1)
        node_all_valid_measurements_mask = torch.all(
            torch.stack((node_features_mask, node_targets_mask), dim=1), dim=1)
        edge_node_all_valid_measurements_mask = torch.logical_and(
            node_all_valid_measurements_mask[edge_index[0]],
            node_all_valid_measurements_mask[edge_index[1]])

        data = Data(
            x=torch.from_numpy(node_features),
            y=torch.from_numpy(node_targets),
            edge_index=edge_index,
            edge_attr=edge_attr,
            h3_index=h3_index,
            aqsid=aqsid,
            x_mask=x_mask,
            y_mask=y_mask,
            node_all_valid_measurements_mask=node_all_valid_measurements_mask,
            edge_node_all_valid_measurements_mask=
            edge_node_all_valid_measurements_mask,
            node_features_mask=node_features_mask,
            node_targets_mask=node_targets_mask,
            timestamps=np.hstack([feature_timestamps, target_timestamps]),
            feature_timestamps=feature_timestamps,
            target_timestamps=target_timestamps,
            feature_start_time=feature_start_time,
            feature_end_time=feature_end_time,
            target_start_time=target_start_time,
            target_end_time=target_end_time,
            freq=self.freq,
            feature_names=self.features,
            target_names=self.targets,
        )
        data.validate()

        return data
