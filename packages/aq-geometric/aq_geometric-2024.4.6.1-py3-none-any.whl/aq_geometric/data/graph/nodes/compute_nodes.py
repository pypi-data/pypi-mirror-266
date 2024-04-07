from datetime import datetime
from typing import List, Union, Callable, Tuple

import h3
import pandas as pd
from aq_utilities.data import apply_filters, filter_aqsids, round_station_lat_lon, filter_lat_lon, remove_duplicate_aqsid, remove_duplicate_lat_lon
from aq_utilities.data import determine_leaf_h3_resolution


def get_nodes_from_df(
    stations_info_df: pd.DataFrame,
    selected_aqsids: Union[List[str], None] = None,
    selected_h3_indices: Union[List[str], None] = None,
    stations_info_filters: List[Callable] = [
        filter_aqsids,
        round_station_lat_lon,
        filter_lat_lon,
        remove_duplicate_aqsid,
        remove_duplicate_lat_lon,
    ],
    min_h3_resolution: int = 0,
    leaf_h3_resolution: Union[int, None] = None,
    max_h3_resolution: int = 12,
    include_root_node: bool = True,
    verbose: bool = False,
) -> Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]]:
    """Get the nodes for the graph from remote."""
    # validate the inputs
    assert min_h3_resolution >= 0, "min_h3_resolution must be greater than or equal to 0"
    assert max_h3_resolution <= 15, "max_h3_resolution must be less than or equal to 15"
    assert min_h3_resolution <= max_h3_resolution, "min_h3_resolution must be less than or equal to max_h3_resolution"
    assert leaf_h3_resolution is None or leaf_h3_resolution >= min_h3_resolution, "leaf_h3_resolution must be greater than or equal to min_h3_resolution"
    assert leaf_h3_resolution is None or leaf_h3_resolution <= max_h3_resolution, "leaf_h3_resolution must be less than or equal to max_h3_resolution"

    if verbose: print(f"[{datetime.now()}] computing nodes")

    df = stations_info_df.copy()

    # get the stations info using the aqsid filter if present
    df = _filter_stations_info(
        df=df,
        selected_aqsids=selected_aqsids,
        stations_info_filters=stations_info_filters,
        verbose=verbose,
    )

    # determine the leaf resolution
    if leaf_h3_resolution is None:
        leaf_h3_resolution = determine_leaf_h3_resolution(
            df=df,
            min_h3_resolution=min_h3_resolution,
            max_h3_resolution=max_h3_resolution,
            verbose=verbose,
        )

    # obtain nodes
    nodes = _get_nodes_for_h3_resolutions(
        df=df,
        selected_h3_indices=selected_h3_indices,
        min_h3_resolution=min_h3_resolution,
        leaf_h3_resolution=leaf_h3_resolution,
        include_root_node=include_root_node,
        as_df=True,
        verbose=verbose,
    )

    return nodes


def _filter_stations_info(
    df: pd.DataFrame,
    selected_aqsids: Union[List[str], None] = None,
    stations_info_filters: List[Callable] = [
        filter_aqsids,
        round_station_lat_lon,
        filter_lat_lon,
        remove_duplicate_aqsid,
        remove_duplicate_lat_lon,
    ],
    verbose: bool = False,
) -> pd.DataFrame:
    """Filter the stations info."""
    if selected_aqsids is not None:
        if verbose:
            print(
                f"[{datetime.now()}] before using selected aqsids {len(df)} stations info"
            )
        df = df[df["aqsid"].isin(selected_aqsids)]
        if verbose:
            print(
                f"[{datetime.now()}] after using selected aqsids {len(df)} stations info"
            )

    if verbose: print(f"[{datetime.now()}] filtering stations info")
    # apply filters if present
    if stations_info_filters is not None and len(stations_info_filters) > 0:
        df = apply_filters(
            df,
            stations_info_filters,
            verbose=verbose,
        )

    return df


def _get_nodes_for_h3_resolutions(
    df: pd.DataFrame,
    min_h3_resolution: int = 0,
    leaf_h3_resolution: int = 9,
    include_root_node: bool = True,
    selected_h3_indices: Union[List[str], None] = None,
    as_df: bool = True,
    verbose: bool = False,
) -> Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]]:
    """Determine the nodes from the given dataframe at each h3 resolution."""

    assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"
    assert "aqsid" in df.columns, "df must have aqsid column"

    if verbose:
        print(f"[{datetime.now()}] computing nodes")

    levels = []
    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for h3_resolution in range(leaf_h3_resolution, min_h3_resolution - 1, -1):
        df_h3 = df.copy(deep=True)
        df_h3["h3_index"] = df_h3.apply(
            lambda x: h3.geo_to_h3(x.latitude, x.longitude, h3_resolution),
            axis=1)
        df_h3 = df_h3.groupby("h3_index").agg({"aqsid": "first"})
        if h3_resolution != leaf_h3_resolution:
            df_h3["aqsid"] = None
        levels.append(df_h3[["aqsid"]])
        if verbose:
            print(
                f"[{datetime.now()}] for resolution {h3_resolution}, we have {len(df_h3)} nodes"
            )
    if include_root_node:
        # add the root node as the mean of all the nodes
        df_h3 = df.copy()
        df_h3["h3_index"] = "root"
        df_h3 = df_h3.groupby("h3_index").agg({"aqsid": "first"})
        if h3_resolution != leaf_h3_resolution:
            df_h3["aqsid"] = None
        levels.append(df_h3[["aqsid"]])

    # make the unified dataframe
    df_lvl = pd.concat(levels, axis=0)
    df_lvl = df_lvl.reset_index()

    if verbose:
        print(
            f"[{datetime.now()}] computed nodes with initial dataframe shape: {df_lvl.shape}"
        )

    df_lvl = df_lvl[["h3_index", "aqsid"]]

    # if selected_h3_indices is not None, filter the h3 indices
    if selected_h3_indices is not None:
        if verbose:
            print(
                f"[{datetime.now()}] before using selected h3 indices {len(df_lvl)} nodes"
            )
        df_lvl = df_lvl[df_lvl["h3_index"].isin(selected_h3_indices)]
        if verbose:
            print(
                f"[{datetime.now()}] after using selected h3 indices {len(df_lvl)} nodes"
            )
        missing_h3_indices = set(selected_h3_indices) - set(df_lvl["h3_index"])
        if verbose:
            print(
                f"[{datetime.now()}] missing h3 indices {missing_h3_indices}")
        if len(missing_h3_indices) > 0:
            df_h3_missing = pd.DataFrame({
                "h3_index": list(missing_h3_indices),
                "aqsid": None
            })
            df_lvl = pd.concat([df_lvl, df_h3_missing], axis=0)
            if verbose:
                print(
                    f"[{datetime.now()}] added missing h3 indices {len(df_h3_missing)} nodes"
                )

    # sort by h3 index
    df_lvl = df_lvl.sort_values(by="h3_index")
    # add the node id
    df_lvl["node_id"] = range(len(df_lvl))  # indexed at 0
    # return as a dataframe
    if as_df:
        return df_lvl
    else:
        return df_lvl.to_numpy()


def _get_nodes_filtered_df(
    df: pd.DataFrame,
    min_h3_resolution: int = 0,
    leaf_h3_resolution: int = 9,
    include_root_node: bool = True,
    selected_h3_indices: Union[List[str], None] = None,
    as_df: bool = True,
    verbose: bool = False,
) -> Union[pd.DataFrame, List[Tuple[Union[str, None], str, int]]]:
    """Process the edges and edge features for the graph."""

    assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"

    if verbose:
        print(f"[{datetime.now()}] processing resolution {leaf_h3_resolution}")
        print(
            f"[{datetime.now()}] after resolution {leaf_h3_resolution}, we have {len(df)} nodes"
        )

    # map the h3 index at the leaf resolution to the station
    df["h3_index"] = df.apply(
        lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution),
        axis=1)
    # store as a dataframe, adding new rows for each resolution
    # if we have a leaf resolution that is too low for the number of stations we take the first
    node_df = df[["aqsid", "h3_index"
                  ]].copy(deep=True).groupby("h3_index").first().reset_index()

    # the aqsid is not meaningful except at the leaf resolution
    df["aqsid"] = None

    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for next_h3_resolution in range(leaf_h3_resolution - 1,
                                    min_h3_resolution - 2, -1):
        if next_h3_resolution < min_h3_resolution: break
        if verbose:
            print(
                f"[{datetime.now()}] processing resolution {next_h3_resolution}"
            )
        # get the h3 index for each station at the next_resolution
        df["next_h3_index"] = df.apply(
            lambda x: h3.h3_to_parent(x.h3_index, next_h3_resolution), axis=1)
        # group by the next h3 index
        df = df.groupby("next_h3_index").aggregate({
            "aqsid": "first"
        }).reset_index()  # we don't need to aggregate the values
        # rename the h3 index to the current h3 index
        df = df.rename(columns={"next_h3_index": "h3_index"})
        # add these new rows to the node_df
        node_df = pd.concat([node_df, df[["aqsid", "h3_index"]]])
        if verbose:
            print(
                f"[{datetime.now()}] after resolution {next_h3_resolution}, we have {len(node_df)} nodes"
            )

    # add another parent node for the entire graph if needed
    if include_root_node:
        if verbose: print(f"[{datetime.now()}] adding root node")
        root_node_id = "root"
        node_df = pd.concat([
            node_df,
            pd.DataFrame({
                "aqsid": [None],
                "h3_index": [root_node_id]
            })
        ])

    # the node id is the index
    node_df["node_id"] = range(len(node_df))
    if verbose: print(f"[{datetime.now()}] processed {len(node_df)} nodes")
    if selected_h3_indices is not None:
        if verbose:
            print(
                f"[{datetime.now()}] before using selected h3 indices {len(node_df)} nodes"
            )
        node_df = node_df[node_df["h3_index"].isin(selected_h3_indices)]
        if verbose:
            print(
                f"[{datetime.now()}] after using selected h3 indices {len(node_df)} nodes"
            )

    # return as a dataframe
    if as_df:
        return node_df
    # return as a list of tuples
    return node_df.to_numpy()
