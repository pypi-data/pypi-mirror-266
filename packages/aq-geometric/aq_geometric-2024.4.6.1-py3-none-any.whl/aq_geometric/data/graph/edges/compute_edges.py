from datetime import datetime
from typing import List, Union, Tuple

import h3

import pandas as pd


def get_edges_from_df(
    stations_info_df: pd.DataFrame,
    min_h3_resolution: int,
    leaf_h3_resolution: int,
    make_undirected: bool,
    include_self_loops: bool,
    with_edge_features: bool,
    selected_h3_indices: Union[List[str], None] = None,
    min_to_root_edge_distance: float = 0.0,
    include_root_node: bool = True,
    as_df: bool = True,
    verbose: bool = False,
) -> Union[List[Tuple[int, int]], List[Tuple[int, int, float]], List[Tuple[
        int, int]]]:
    """Process the edges and edge features for the graph."""
    assert "latitude" in stations_info_df.columns and "longitude" in stations_info_df.columns, "stations_info_df must have latitude and longitude columns"

    # we have one more more stations with the exact same location as another station, so we need to drop one of them
    df = stations_info_df.copy(deep=True).groupby(["latitude",
                                                   "longitude"]).aggregate({
                                                       "aqsid":
                                                       "first"
                                                   }).reset_index()

    if verbose:
        print(f"[{datetime.now()}] processing resolution {leaf_h3_resolution}")
    # map the h3 index at the leaf resolution to the station
    df["h3_index"] = df.apply(
        lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution),
        axis=1)
    # if the leaf resolution is too low for the number of stations we take the unique h3 indices
    df = df.groupby("h3_index").aggregate({"aqsid": "first"}).reset_index()

    edges = [
    ]  # tuples of (h3_index1, h3_index2), when concatenated will be shape (2, num_edges)
    edge_attr = [
    ]  # tuples of (h3_index1, h3_index2, distance), when concatenated will be shape (num_edges, 1)
    node_counter = 0  # counter for the node ids

    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for next_h3_resolution in range(leaf_h3_resolution - 1,
                                    min_h3_resolution - 2, -1):
        # add edges for the current resolution
        node_counter += len(df["h3_index"].values)
        current_resolution_nodes = set(df["h3_index"].unique().tolist())
        for _, row in df.iterrows():
            # we already have all h3 indices at this resolution, but we need to see if any of them are neighbors
            # get the neighbors of the current h3 index
            neighbors = h3.k_ring(row.h3_index, 1)
            # check if any of the neighbors are in the current resolution. note that k_ring returns the current h3 index as well
            if any([
                    n in current_resolution_nodes for n in neighbors
                    if n != row.h3_index
            ]):
                # add the edges
                for n in neighbors:
                    if n in current_resolution_nodes:
                        if n == row.h3_index and include_self_loops:
                            edges.append((row.h3_index, n))
                            if with_edge_features:
                                edge_attr.append((row.h3_index, n, 0))
                            if make_undirected:
                                edges.append((n, row.h3_index))
                                if with_edge_features:
                                    edge_attr.append((row.h3_index, n, 0))
                        elif n != row.h3_index:
                            edges.append((row.h3_index, n))
                            if make_undirected: edges.append((n, row.h3_index))
                            # we need to get lat-lon for the distance calculation
                            if with_edge_features:
                                lat1, lon1 = h3.h3_to_geo(row.h3_index)
                                lat2, lon2 = h3.h3_to_geo(n)
                                distance = h3.point_dist((lat1, lon1),
                                                         (lat2, lon2))
                                edge_attr.append((row.h3_index, n, distance))
                                if make_undirected:
                                    edge_attr.append(
                                        (n, row.h3_index, distance))

        if next_h3_resolution < min_h3_resolution: break
        if verbose:
            print(
                f"[{datetime.now()}] processing resolution {next_h3_resolution}"
            )
        # get the h3 index for each station at the next_resolution
        df["next_h3_index"] = df.apply(
            lambda x: h3.h3_to_parent(x.h3_index, next_h3_resolution), axis=1)
        # add edges for the next resolution
        edges.extend(df[["h3_index", "next_h3_index"
                         ]].apply(lambda x: (x.h3_index, x.next_h3_index),
                                  axis=1).values)
        if make_undirected:
            edges.extend(df[["h3_index", "next_h3_index"
                             ]].apply(lambda x: (x.next_h3_index, x.h3_index),
                                      axis=1).values)
        if with_edge_features:
            new_edge_attrs = [
                (v[0], v[1],
                 h3.point_dist(h3.h3_to_geo(v[0]), h3.h3_to_geo(v[1])))
                for v in df[["h3_index", "next_h3_index"]].to_numpy()
            ]
            edge_attr.extend(new_edge_attrs)
            if make_undirected:
                edge_attr.extend([(v[1], v[0], v[2]) for v in new_edge_attrs])
        # group by the next h3 index
        df = df.groupby("next_h3_index").aggregate({
            "aqsid": "first"
        }).reset_index()  # we don't need to aggregate the values
        # rename the h3 index to the current h3 index
        df = df.rename(columns={"next_h3_index": "h3_index"})

    # add another parent node for the entire graph if needed
    if include_root_node:
        if verbose: print(f"[{datetime.now()}] adding root node")
        root_node_id = "root"
        edges.extend([(root_node_id, n) for n in df["h3_index"].values])
        if with_edge_features:
            edge_attr.extend([(n, root_node_id, min_to_root_edge_distance)
                              for n in df["h3_index"].values
                              ])  # for now we have 0 for the distance

    if verbose: print(f"[{datetime.now()}] processed {len(edges)} edges")

    # only return the selected h3 indices if needed
    if selected_h3_indices is not None:
        edges = [
            e for e in edges
            if e[0] in selected_h3_indices and e[1] in selected_h3_indices
        ]
        if with_edge_features:
            edge_attr = [
                e for e in edge_attr
                if e[0] in selected_h3_indices and e[1] in selected_h3_indices
            ]

    # return as a pd.DataFrame
    if as_df:
        if with_edge_features:
            return pd.DataFrame(edges, columns=["from", "to"]), pd.DataFrame(
                edge_attr, columns=["from", "to", "distance"])
        else:
            return pd.DataFrame(edges, columns=["from", "to"])
    # return as a list of tuples
    if with_edge_features:
        assert len(edges) == len(edge_attr)
        return edges, edge_attr
    else:
        return edges
