import os
import os.path as osp
from datetime import datetime
from typing import Tuple, List, Union, Callable, Dict

import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Dataset, Data
from aq_utilities.engine.psql import get_engine
from aq_utilities.data import load_hourly_data, load_hourly_feature, load_hourly_features, load_stations_info, load_daily_stations
from aq_utilities.data import apply_filters, filter_aqsids, round_station_lat_lon, filter_lat_lon, remove_duplicate_aqsid, remove_duplicate_lat_lon
from aq_utilities.data import measurements_to_aqsid, determine_leaf_h3_resolution

from aq_geometric.data.remote import load_node_feature, load_node_features, load_nodes_info
from aq_geometric.data.file.local import load_hourly_data_from_fp, load_stations_info_from_fp, load_hourly_feature_from_fp, load_hourly_features_from_fp
from aq_geometric.data.graph.edges.compute_edges import get_edges_from_df
from aq_geometric.data.graph.nodes.compute_nodes import get_nodes_from_df
from aq_geometric.data.graph.nodes.compute_node_features import data_to_feature, get_node_feature, get_node_features, stack_node_features
from aq_geometric.data.graph.compute_graph import make_graph


class AqGeometricDataset(Dataset):
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
            max_samples_in_graph_on_disk: int = 380,
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
        self.max_samples_in_graph_on_disk = max_samples_in_graph_on_disk
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

        # obtain the timestamps for the features and targets
        self.timestamps = pd.date_range(
            start=self.start_time, end=self.end_time, freq=self.freq,
            inclusive="left" if self.time_closed_interval == False else "both")
        # save the length as the number of time steps minus the number of samples in the node feature minus the number of samples in the node target
        self.num_graphs = 1 + len(
            self.timestamps
        ) - self.num_samples_in_node_features - self.num_samples_in_node_targets

        # determine the number of graphs based on start_time, end_time and max_samples_in_graph_on_disk
        q_start_time, q_end_time = self.timestamps[
            0], self.timestamps[-1] + pd.Timedelta(
                self.freq)  # add one more sample to the end time
        query_start_times = [q_start_time]
        query_end_times = [q_end_time]

        if self.max_samples_in_graph_on_disk < len(self.timestamps):
            query_start_times = self.timestamps[::self.
                                                max_samples_in_graph_on_disk].tolist(
                                                )
            query_end_times = self.timestamps[
                self.max_samples_in_graph_on_disk::self.
                max_samples_in_graph_on_disk].tolist()
            query_start_times.append(query_end_times[-1])
            query_end_times.append(
                pd.to_datetime(self.timestamps[-1]) + pd.Timedelta(self.freq))
        # persist the start and end times
        self.query_start_times = query_start_times
        self.query_end_times = query_end_times

        self.graph_index_ranges = []
        self.current_graph_index = None
        self.current_graph = None
        self.stations_info_df = None
        self.nodes = None
        self.edges = None
        self.edge_attr = None
        self.num_graphs_on_disk = 0
        self._loaded_graph_indices = set()
        self._graph = None

        super().__init__(root, transform, pre_transform, pre_filter)

        # override the __getitem__ method
        self.__getitem__ = self.__sharded_getitem__

    @property
    def raw_file_names(self) -> List[str]:
        """Return the raw file name of the data and stations info."""
        from glob import glob
        raw_fps = ["stations_info.csv"]
        # extend the raw file names with the hourly features and targets
        raw_fps.extend([
            osp.basename(f) for f in list(
                glob(osp.join(self.raw_dir, f"*_{f}_data.csv"))
                for f in self.features) for f in f
        ])
        raw_fps.extend([
            osp.basename(f) for f in list(
                glob(osp.join(self.raw_dir, f"*_{f}_data.csv"))
                for f in self.targets if f not in self.features) for f in f
        ])
        return raw_fps

    @property
    def processed_file_names(self) -> List[str]:
        """Return the processed file names."""
        from glob import glob
        return [
            osp.basename(f)
            for f in glob(osp.join(self.processed_dir, "data_*.pt"))
        ]

    def clear(self):
        """Clear the raw and processed directories."""
        import shutil
        shutil.rmtree(self.raw_dir)
        shutil.rmtree(self.processed_dir)
        return None

    def download(self):
        """Query remote database for the data and stations info, saving to csv files."""
        # ensure the processed directory exists
        if not osp.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
        # check if the there are already raw files
        if len(os.listdir(self.raw_dir)) > 0:
            print(f"Raw files already exist in {self.raw_dir}")
            return

        timestamps = self.timestamps
        # assert that the number of samples in the node feature and target is less than the total number of samples
        assert self.num_samples_in_node_features + self.num_samples_in_node_targets <= len(
            timestamps
        ), "The number of samples in the node feature and target must be less than the total number of samples."
        start_time, end_time = timestamps[0], timestamps[-1] + pd.Timedelta(
            self.freq)  # add one more sample to the end time

        if self.verbose:
            print(f"timestamps: {self.timestamps}")
            print(f"start times: {self.query_start_times}")
            print(f"end times: {self.query_end_times}")

        stations_info = load_daily_stations(
            engine=self.engine,
            query_date=start_time.strftime("%Y-%m-%d"),
            selected_aqsids=self.selected_aqsids,
            verbose=self.verbose,
        )
        # apply filters
        stations_info = apply_filters(
            stations_info,
            self.stations_info_filters,
            verbose=self.verbose,
        )
        # determine leaf resolution if none is provided
        if self.leaf_h3_resolution is None:
            leaf_resolution = determine_leaf_h3_resolution(
                df=stations_info,
                min_h3_resolution=self.min_h3_resolution,
                max_h3_resolution=self.max_h3_resolution,
                verbose=self.verbose,
            )
            if self.verbose:
                print(f"[{datetime.now()}] leaf resolution: {leaf_resolution}")
            self.leaf_h3_resolution = leaf_resolution

        # save the stations info
        stations_info.to_csv(osp.join(self.raw_dir, "stations_info.csv"),
                             index=False)

        # determine the set of features and targets
        features_and_targets = set(self.features + self.targets)
        # load the hourly features and targets
        for f in features_and_targets:
            for i, (q_start_time, q_end_time) in enumerate(
                    zip(self.query_start_times, self.query_end_times)):
                data_df = load_node_feature(
                    engine=self.engine,
                    table="hourly_data",
                    start_time=q_start_time,
                    end_time=q_end_time,
                    feature=f,
                    selected_aqsids=self.selected_aqsids,
                    verbose=self.verbose,
                )
                feature_df = data_to_feature(
                    df=data_df,
                    stations_info_df=stations_info,
                    min_h3_resolution=self.min_h3_resolution,
                    leaf_h3_resolution=self.leaf_h3_resolution,
                    verbose=self.verbose,
                )
                # save the hourly features and targets
                feature_df.to_csv(osp.join(self.raw_dir, f"{f}_data_{i}.csv"),
                                  index=False)
        return None

    def process(self):
        """Process the data and stations info into individual graphs."""
        # ensure the processed directory exists
        if not osp.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        # check if the there are already processed files
        if len(os.listdir(self.processed_dir)) > 2:
            print(f"Processed files already exist in {self.processed_dir}")
            return

        # obtain the timestamps for the features and targets
        q_start_times, q_end_times = self.query_start_times, self.query_end_times

        if self.verbose:
            print(
                f"[{datetime.now()}] start and end times: {[(start_time, end_time) for start_time, end_time in zip(q_start_times, q_end_times)]}"
            )

        num_graphs_on_disk = len(q_start_times)

        if self.verbose:
            print(f"[{datetime.now()}] processing {num_graphs_on_disk} graphs")

        for i, (start_time,
                end_time) in enumerate(zip(q_start_times, q_end_times)):
            if self.stations_info_df is None:
                stations_info_df = pd.read_csv(
                    osp.join(self.raw_dir, "stations_info.csv"))
                self.stations_info_df = stations_info_df
            if self.leaf_h3_resolution is None:
                # determine leaf resolution if none is provide
                leaf_resolution = determine_leaf_h3_resolution(
                    df=self.stations_info_df,
                    min_h3_resolution=self.min_h3_resolution,
                    max_h3_resolution=self.max_h3_resolution,
                    verbose=self.verbose,
                )
                if self.verbose:
                    print(
                        f"[{datetime.now()}] leaf resolution: {leaf_resolution}"
                    )
                self.leaf_h3_resolution = leaf_resolution
            if self.nodes is None:
                # get the h3_index_to_node_id_map and h3_index_to_aqsid_map
                nodes = get_nodes_from_df(
                    stations_info_df=self.stations_info_df,
                    min_h3_resolution=self.min_h3_resolution,
                    leaf_h3_resolution=self.leaf_h3_resolution,
                    include_root_node=self.include_root_node,
                    verbose=self.verbose,
                )
                self.nodes = nodes
            if self.edges is None:
                # get the edges and edge attributes
                edges = get_edges_from_df(
                    stations_info_df=self.stations_info_df,
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
                    self.edges, self.edge_attr = edges
                else:
                    self.edges = edges
            # make the timestamps between start_time and end_time
            graph_timestamps = pd.date_range(start=start_time, end=end_time,
                                             freq=self.freq, inclusive="left")

            # load node features from disk
            node_features = []
            # load the node features from the local file
            for feature in self.features:
                feature_fp = osp.join(self.raw_dir, f"{feature}_data_{i}.csv")
                feature_df = load_hourly_feature_from_fp(feature_fp)
                feature = get_node_feature(
                    feature_df=feature_df,
                    timestamps=graph_timestamps,
                    nodes=self.nodes,
                    verbose=self.verbose,
                )
                node_features.append(feature)
            # load node targets from disk
            node_targets = []
            # load the node features from the local file
            for feature in self.targets:
                feature_fp = osp.join(self.raw_dir, f"{feature}_data_{i}.csv")
                feature_df = load_hourly_feature_from_fp(feature_fp)
                feature = get_node_feature(
                    feature_df=feature_df,
                    timestamps=graph_timestamps,
                    nodes=self.nodes,
                    verbose=self.verbose,
                )
                node_targets.append(feature)
            # stack the features and targets
            node_features = stack_node_features(self.nodes, node_features)
            node_targets = stack_node_features(self.nodes, node_targets)
            # make the graph
            graph = make_graph(
                nodes=self.nodes,
                edges=self.edges[["from", "to"]].to_numpy().T,
                edge_attr=self.edge_attr.drop(
                    columns=["from", "to"]).to_numpy()
                if self.edge_attr is not None else None,
                node_features=node_features,
                targets=node_targets,
                timestamps=graph_timestamps,
                feature_names=self.features,
                target_names=self.targets,
                node_missing_value=self.node_missing_value,
                verbose=self.verbose,
            )
            if self.pre_transform is not None:
                if self.verbose:
                    print(
                        f"Pre-transforming graph {i} of {num_graphs_on_disk}")
                graph = self.pre_transform(graph)

            # when saving the graph, in the single-file case we want the end index to be the number of timestamps
            torch.save(graph, osp.join(self.processed_dir, f'data_{i}.pt'))
            self.graph_index_ranges.append((start_time, end_time))
            if self.verbose:
                print(f"Processed graph on disk {i+1} of {num_graphs_on_disk}")
                print(f"Graph start time {start_time}, end time {end_time}.")
            self.num_graphs_on_disk += 1  # increment the number of graphs on disk

    def len(self):
        return self.num_graphs  # based on the number of timestamps

    def get(self, idx):
        # ensure we have the graph index ranges
        # get the processed file names
        if self.num_graphs_on_disk == 0:
            self.num_graphs_on_disk = len(self.processed_file_names)
        # map idx to the graph on disk
        i = idx // self.max_samples_in_graph_on_disk
        if self.verbose:
            print(
                f"[{datetime.now()}] Getting graph {i+1} of {self.num_graphs_on_disk+1}"
            )

        self._load_graph_from_disk(i)
        return self.__sharded_getitem__(idx)

    def __sharded_getitem__(self, idx):
        """Compute the graph for index idx using data from disk."""
        # get the data for this range
        time_index_start = idx % self.max_samples_in_graph_on_disk  # determine the start index relative to the graph
        time_index_end = time_index_start + self.num_samples_in_node_features + self.num_samples_in_node_targets

        data = self._load_data_from_memory(time_index_start, time_index_end)

        if self.transform is not None:
            data = self.transform(data)

        return data

    def _load_graph_from_disk(self, i):
        """Load the graph from disk."""
        if i not in self._loaded_graph_indices:
            # remove the existing graph from memory
            self._graph = None
            # remove the existing graph index
            self._loaded_graph_indices = set()

            # load the graph from disk and next graph if available
            graph = torch.load(osp.join(self.processed_dir, f'data_{i}.pt'))
            self._loaded_graph_indices.add(i)
            if self.verbose:
                print(f"Loaded graph {i+1} of {self.num_graphs_on_disk+1}")
            if i < self.num_graphs_on_disk - 1:
                # obtain the next graph
                next_graph = torch.load(
                    osp.join(self.processed_dir, f'data_{i+1}.pt'))
                if self.verbose:
                    print(f"Loaded graph {i+2} of {self.num_graphs_on_disk+1}")
                # ensure the h3_index and aqsid are the same
                assert all(h1 == h2 for h1, h2 in zip(
                    graph.h3_index.tolist(), next_graph.h3_index.tolist())
                           ), "The h3_index must be the same for both graphs."
                assert all(h1 == h2 for h1, h2 in zip(
                    graph.aqsid.tolist(), next_graph.aqsid.tolist())
                           ), "The aqsid must be the same for both graphs."
                # concatenate the graphs
                node_features = torch.cat((graph.x, next_graph.x), dim=1)
                node_targets = torch.cat((graph.y, next_graph.y), dim=1)
                # invariant
                h3_index = graph.h3_index
                aqsid = graph.aqsid
                # combine the masks
                x_mask = torch.cat((graph.x_mask, next_graph.x_mask), dim=1)
                y_mask = torch.cat((graph.y_mask, next_graph.y_mask), dim=1)
                # determine the aggregate time range
                feature_start_time = graph.feature_start_time
                feature_end_time = next_graph.feature_end_time
                target_start_time = graph.target_start_time
                target_end_time = next_graph.target_end_time
                # make the new graph
                graph = Data(
                    x=node_features,
                    y=node_targets,
                    edge_index=graph.edge_index,
                    edge_attr=graph.edge_attr,
                    h3_index=h3_index,
                    aqsid=aqsid,
                    x_mask=x_mask,
                    y_mask=y_mask,
                    feature_start_time=feature_start_time,
                    feature_end_time=feature_end_time,
                    target_start_time=target_start_time,
                    target_end_time=target_end_time,
                )
                self._loaded_graph_indices.add(i + 1)
                if self.verbose:
                    print(f"Combined graph {i+1} and {i+2}")
                    print(
                        f"Current loaded graph indices (0 based, subtract one): {self._loaded_graph_indices}"
                    )
            # save the current data to memory
            self._graph = graph
        else:
            if self.verbose:
                print(f"Graph {i+1} already loaded.")
                print(
                    f"Current loaded graph indices (0 based, subtract one): {self._loaded_graph_indices}"
                )

    def _load_data_from_memory(
        self,
        time_index_start: int,
        time_index_end: int,
    ) -> Data:
        """Load some or all of the graph from memory."""
        # we static edge_index and edge_attr
        edge_index = self._graph.edge_index
        edge_attr = self._graph.edge_attr

        # we need to compute the feature and target start and end times
        feature_start_time = pd.to_datetime(
            self._graph.feature_start_time) + (pd.Timedelta(self.freq) *
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
        node_features = self._graph.x[:, start_idx:start_idx +
                                      self.num_samples_in_node_features].numpy(
                                      )
        node_targets = self._graph.y[:, start_idx +
                                     self.num_samples_in_node_features:
                                     end_idx].numpy()
        # handle missing values
        node_features = np.nan_to_num(node_features,
                                      nan=self.node_missing_value)
        node_targets = np.nan_to_num(node_targets, nan=self.node_missing_value)

        # get the node mapping attributes from the current graph
        h3_index = self._graph.h3_index
        aqsid = self._graph.aqsid

        x_mask = self._graph.x_mask[:, start_idx:start_idx +
                                    self.num_samples_in_node_features]
        y_mask = self._graph.y_mask[:, start_idx +
                                    self.num_samples_in_node_features:end_idx]

        if self.verbose:
            # print shapes
            print(f"node_features shape: {node_features.shape}")
            print(f"node_targets shape: {node_targets.shape}")
            print(f"x_mask shape: {x_mask.shape}")
            print(f"y_mask shape: {y_mask.shape}")
            print(f"edge_index shape: {edge_index.shape}")
            print(
                f"edge_attr shape: {edge_attr.shape if edge_attr is not None else None}"
            )

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
