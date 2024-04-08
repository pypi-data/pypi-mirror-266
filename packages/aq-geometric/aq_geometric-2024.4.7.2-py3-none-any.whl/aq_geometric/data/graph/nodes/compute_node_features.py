from datetime import datetime
from typing import List, Union, Tuple

import h3
import numpy as np
import pandas as pd

from aq_geometric.data.reindex.features import ensure_feature_axis
from aq_geometric.data.filter.node_features import filter_features_by_measurement


def get_node_feature(
    feature_df: pd.DataFrame,
    nodes: pd.DataFrame,
    timestamps: Union[pd.DatetimeIndex, np.ndarray],
    verbose: bool = False,
) -> List[pd.DataFrame]:
    """Load a feature for the nodes."""
    assert "h3_index" in nodes.columns, "nodes must have a h3_index column"
    assert "timestamp" in feature_df.columns, "feature_df must have a timestamp column"
    assert "h3_index" in feature_df.columns, "feature_df must have a h3_index column"
    assert "value" in feature_df.columns, "feature_df must have a value column"

    # ensure that the data type is correct
    feature_df["timestamp"] = pd.to_datetime(feature_df["timestamp"],
                                             unit='ms')
    timestamps = pd.to_datetime(timestamps)
    if verbose:
        print(
            f"[{datetime.now()}] before pivot {feature_df.notna().sum().sum()} values are not nan (shape {feature_df.shape})"
        )

    # resample to match the timestamps
    multi_index = pd.MultiIndex.from_product([timestamps, nodes.h3_index],
                                             names=["timestamp", "h3_index"])
    # ensure that the feature axis is the same as the node axis
    feature_df = feature_df.set_index(["timestamp", "h3_index"])
    if verbose:
        print(
            f"[{datetime.now()}] after set_index {feature_df.notna().sum().sum()} values are not nan (shape {feature_df.shape})"
        )
    feature_df = feature_df.reindex(multi_index)
    if verbose:
        print(
            f"[{datetime.now()}] after reindex {feature_df.notna().sum().sum()} values are not nan (shape {feature_df.shape})"
        )
    feature_df = feature_df.reset_index()
    feature_df = feature_df.pivot(index="h3_index", columns="timestamp",
                                  values="value")
    if verbose:
        print(
            f"[{datetime.now()}] after pivot {feature_df.notna().sum().sum()} values are not nan (shape {feature_df.shape})"
        )

    return feature_df


def get_node_features(
    nodes: Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]],
    start_time: str,
    end_time: str,
    freq: str,
    features_df: Union[pd.DataFrame, None] = None,
    features: Union[List[str], None] = None,
    feature_dfs: Union[List[pd.DataFrame], None] = None,
    time_interval_closed: bool = False,
    as_df: bool = True,
    verbose: bool = False,
) -> Union[List[pd.DataFrame], List[np.ndarray]]:
    """Get features for nodes."""
    # ensure we have at least one of feature_df or feature_dfs
    assert features_df is not None or feature_dfs is not None, "either feature_df or feature_dfs must be provided"

    if features_df is not None:
        assert feature_dfs is None, "feature_dfs must be None if feature_df is provided"
        assert features is not None, "features must be provided if feature_dfs is a dataframe"
        assert isinstance(features, list), "features must be a list"
        assert len(features) > 0, "features must have at least one element"
    if feature_dfs is not None:
        assert len(features) == len(
            feature_dfs), "features must be the same length as feature_dfs"
        assert isinstance(feature_dfs, list), "feature_dfs must be a list"
        assert len(
            feature_dfs) > 0, "feature_dfs must have at least one element"
        assert "h3_index" in feature_dfs[
            0].columns, "feature_dfs must have a h3_index column"
        assert "timestamp" in feature_dfs[
            0].columns, "feature_dfs must have a timestamp column"
        assert "value" in feature_dfs[
            0].columns, "feature_dfs must have a value column"

    node_feature_dfs = []
    if feature_dfs is not None:
        node_feature_dfs.extend(
            _get_node_features_from_dfs(
                nodes=nodes,
                start_time=start_time,
                end_time=end_time,
                freq=freq,
                feature_dfs=feature_dfs,
            ))
    else:
        node_feature_dfs.extend(
            _get_node_features_from_df(
                nodes=nodes,
                start_time=start_time,
                end_time=end_time,
                freq=freq,
                features_df=features_df,
                features=features,
                time_interval_closed=time_interval_closed,
                verbose=verbose,
            ))

    if as_df:
        return node_feature_dfs
    else:
        return [df.values for df in node_feature_dfs]


def stack_node_features(
    nodes: Union[pd.DataFrame, np.ndarray],
    node_features: Union[List[pd.DataFrame], List[np.ndarray]],
    verbose: bool = False,
) -> pd.DataFrame:
    """Stack the node features."""
    assert isinstance(node_features, list), "node_features must be a list"
    assert len(
        node_features) > 0, "node_features must have at least one element"
    assert isinstance(node_features[0], pd.DataFrame) or isinstance(
        node_features[0],
        np.ndarray), "node_features must be a list of dataframes or arrays"
    assert isinstance(nodes, pd.DataFrame) or isinstance(
        nodes, np.ndarray), "nodes must be a dataframe or array"

    if isinstance(nodes, np.ndarray):
        nodes = pd.DataFrame(nodes, columns=["h3_index", "aqsid", "node_id"])

    # check that the h3 indexes match across dataframes
    node_h3_index_list = nodes["h3_index"].to_list()
    for i in range(len(node_features)):
        if isinstance(node_features[i], pd.DataFrame):
            node_feature_h3_index_list = node_features[i].index.to_list()
            assert node_h3_index_list == node_feature_h3_index_list, "node h3 indexes must match"
        else:
            assert node_features[i].shape[0] == nodes.shape[
                0], "node features must have the same number of rows as nodes"

    if verbose:
        print(
            f"[{datetime.now()}] stacking {len(node_features)} node features")
    if isinstance(node_features[0], pd.DataFrame):
        return np.stack([df.values for df in node_features], axis=2)
    else:
        return np.stack(node_features, axis=2)


def data_to_feature(
    df: pd.DataFrame,
    stations_info_df: pd.DataFrame,
    min_h3_resolution: int = 0,
    leaf_h3_resolution: int = 9,
    include_root_node: bool = True,
    verbose: bool = False,
) -> pd.DataFrame:
    """Process hourly data to an h3-indexed feature."""
    assert "aqsid" in df.columns, "aqsid must be in the dataframe"
    assert "timestamp" in df.columns, "timestamp must be in the dataframe"
    assert "value" in df.columns, "value must be in the dataframe"
    assert "aqsid" in stations_info_df.columns, "aqsid must be in the stations_info dataframe"

    if verbose:
        print(f"[{datetime.now()}] before join df has shape {df.shape}")

    # join on the aqsid such that the lat and lon are available for hourly data
    df = df.join(stations_info_df.set_index("aqsid"), on="aqsid")

    if verbose:
        print(f"[{datetime.now()}] after join df has shape {df.shape}")

    # store the h3-indexed features at each level as a list of dataframes
    levels = []

    if verbose:
        print(
            f"[{datetime.now()}] processing resolutions between {leaf_h3_resolution} and {min_h3_resolution} inclusive with root set to {include_root_node}"
        )

    for i in range(leaf_h3_resolution, min_h3_resolution - 1, -1):
        h3_df = df.copy()
        h3_df["timestamp"] = pd.to_datetime(h3_df["timestamp"])
        h3_df["h3_index"] = df.apply(
            lambda x: h3.geo_to_h3(x.latitude, x.longitude, i), axis=1)
        h3_df = h3_df.groupby(["h3_index",
                               "timestamp"]).mean(numeric_only=True)
        levels.append(h3_df[["value"]])
        if verbose:
            print(
                f"[{datetime.now()}] after processing resolution {i}, h3_df has shape {h3_df.shape}"
            )

    if include_root_node:
        # add the root node as the mean of all the nodes
        root_df = df.copy()
        root_df["timestamp"] = pd.to_datetime(root_df["timestamp"])
        root_df["h3_index"] = "root"
        root_df = root_df.groupby(["h3_index",
                                   "timestamp"]).mean(numeric_only=True)
        levels.append(root_df[["value"]])
        if verbose:
            print(
                f"[{datetime.now()}] after processing root node, root_df has shape {root_df.shape}"
            )

    # concatinate all dataframes in levels
    df_lvl = pd.concat(levels, axis=0)
    if verbose:
        print(
            f"[{datetime.now()}] after concatenating levels, df_lvl has shape {df_lvl.shape}"
        )
    df_lvl.reset_index(inplace=True)

    if verbose:
        print(
            f"[{datetime.now()}] after reset_index, df_lvl has shape {df_lvl.shape}"
        )

    df_lvl = df_lvl.drop_duplicates(subset=["h3_index", "timestamp"],
                                    keep="first")

    if verbose:
        print(
            f"[{datetime.now()}] after dropping duplicates, df_lvl has shape {df_lvl.shape}"
        )

    return df_lvl


def _process_node_feature(
    feature_df: pd.DataFrame,
    nodes: Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]],
    missing_value: float = np.nan,
    as_df: bool = False,
    verbose: bool = False,
) -> Union[pd.DataFrame, List[np.ndarray]]:
    """Obtain features for the nodes from the feature_df.
    
    The feature df contains one feature indexed by h3_index. We want to
    ensure that we have the feature values for each node. This may result in
    nodes with missing values for the features, which are filled using the
    missing_value parameter.

    Args:
        features_df: pd.DataFrame: the dataframe to re-index
        nodes: pd.DataFrame or List[Tuple[Union[str, None], str, int]]: the nodes
        missing_value: float: the value to fill missing values with
        as_df: bool: whether to return as a dataframe or list of arrays
        verbose: bool: whether to print debug information

    Returns:
        pd.DataFrame or np.ndarray: the node feature values dataframe or list of arrays
    """
    # we assume that the dataframe has columns for the aqsid, h3_index and node_id
    # if nodes is an array, it is of shape (num_nodes, 3) with columns (aqsid, h3_index, node_id)
    if verbose:
        print(
            f"[{datetime.now()}] before re-indexing re-indexing to node h3 indices, feature_df has shape {feature_df.shape}"
        )
    if not isinstance(nodes, pd.DataFrame):
        nodes_df = pd.DataFrame(nodes,
                                columns=["h3_index", "aqsid", "node_id"])
    else:
        nodes_df = nodes.copy(deep=True)

    if verbose:
        print(f"[{datetime.now()}] nodes_df has shape {nodes_df.shape}")

    # join the dataframes using the h3_index
    nodes_df = nodes_df.merge(feature_df, on="h3_index",
                              how="left").fillna(missing_value)

    if verbose:
        print(
            f"[{datetime.now()}] after join nodes_df has shape {nodes_df.shape}"
        )

    # drop the aqsid and h3_index columns
    nodes_df.drop(columns=["node_id", "aqsid", "h3_index"], inplace=True)
    if verbose: print(f"[{datetime.now()}] processed dataframe")
    if verbose:
        print(
            f"[{datetime.now()}] after re-indexing to node h3 indices, nodes_df has shape {nodes_df.shape}"
        )

    # return as a dataframe
    if as_df:
        return nodes_df
    # return as a list of arrays
    return nodes_df.values


def _get_node_features_from_df(
    nodes: Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]],
    start_time: str,
    end_time: str,
    freq: str,
    features_df: Union[pd.DataFrame, None] = None,
    features: Union[List[str], None] = None,
    time_interval_closed: bool = False,
    verbose: bool = False,
) -> List[pd.DataFrame]:
    """Get features for nodes."""
    feature_dfs = []
    timestamps = pd.date_range(
        start=start_time, end=end_time, freq=freq,
        inclusive="left" if time_interval_closed == False else "both")

    h3_indices = []
    if isinstance(nodes, pd.DataFrame):
        h3_indices = nodes["h3_index"].unique().tolist()
    else:
        h3_indices = [n[0] for n in nodes]

    for feature in features:

        if verbose: print(f"[{datetime.now()}] loading feature {feature}")

        feature_df = filter_features_by_measurement(
            features_df=features_df,
            feature=feature,
            feature_start_time=start_time,
            feature_end_time=end_time,
        )
        # do not include the measurement column
        feature_df.drop(columns=["measurement"], inplace=True)

        if verbose:
            print(
                f"[{datetime.now()}] loaded feature {feature} with shape {feature_df.shape}"
            )

        feature_dfs.append(
            get_node_feature(
                feature_df=feature_df,
                nodes=nodes,
                feature_timestamps=timestamps,
                h3_indices=h3_indices,
                verbose=verbose,
            ))

    return feature_dfs


def _get_node_features_from_dfs(
    nodes: Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]],
    start_time: str,
    end_time: str,
    freq: str,
    feature_dfs: Union[pd.DataFrame, None] = None,
    time_interval_closed: bool = False,
    verbose: bool = False,
) -> Union[List[pd.DataFrame], List[np.ndarray]]:
    """Get features for nodes."""
    timestamps = pd.date_range(
        start=start_time, end=end_time, freq=freq,
        inclusive="left" if time_interval_closed == False else "both")

    h3_indices = []
    if isinstance(nodes, pd.DataFrame):
        h3_indices = nodes["h3_index"].unique().tolist()
    else:
        h3_indices = [n[1] for n in nodes]

    for feature_df in feature_dfs:

        if verbose:
            print(
                f"[{datetime.now()}] loaded feature with shape {feature_df.shape}"
            )

        feature_dfs.append(
            get_node_feature(
                feature_df=feature_df,
                nodes=nodes,
                feature_timestamps=timestamps,
                h3_indices=h3_indices,
                verbose=verbose,
            ))

    return feature_dfs
