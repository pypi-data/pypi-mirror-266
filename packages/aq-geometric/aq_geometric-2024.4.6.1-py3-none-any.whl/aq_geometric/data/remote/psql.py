from datetime import datetime
from typing import List, Union

import pandas as pd
from aq_utilities.data import load_hourly_data, load_hourly_feature, load_hourly_features, load_stations_info, load_daily_stations


def load_nodes_info(
    engine: "sqlalchemy.engine.Engine",
    query_date: str,
    selected_aqsids: Union[List[str], None] = None,
    table: str = "daily_stations",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load stations info from the database.
    
    Args:
        engine: sqlalchemy.engine.Engine: the database engine
        date: str: the date to load the data for
        selected_aqsids: List[str] or None: the aqsids to load

    Returns:
        pd.DataFrame or str: the stations info or an error message
    """
    assert table in ["daily_stations", "stations_info"
                     ], "table must be daily_stations or stations_info"

    if verbose:
        print(f"[{datetime.now()}] loading stations info from table {table}")

    # load the stations info
    stations_info = pd.DataFrame()
    if table == "daily_stations":
        stations_info = load_daily_stations(engine=engine,
                                            query_date=query_date,
                                            selected_aqsids=selected_aqsids,
                                            verbose=verbose)
    elif table == "stations_info":
        stations_info = load_stations_info(engine=engine,
                                           query_date=query_date,
                                           selected_aqsids=selected_aqsids,
                                           verbose=verbose)

    if verbose:
        print(
            f"[{datetime.now()}] loaded {len(stations_info)} stations info from table {table}"
        )

    return stations_info


def load_node_feature(
    engine: "sqlalchemy.engine.Engine",
    start_time: str,
    end_time: str,
    feature: str,
    selected_aqsids: Union[List[str], None] = None,
    selected_h3_indices: Union[List[str], None] = None,
    table: str = "hourly_features",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load node feature from the database.
    
    Load the processed feature indexed by aqsids or h3 indices.
    Returns a dataframes in long format, with columns for the 
    aqsid or h3 index, the feature, and the value.

    Args:
        engine: sqlalchemy.engine.Engine: the database engine
        start_time: str: the start time to load the data for
        end_time: str: the end time to load the data for
        feature: str: the feature to load
        selected_aqsids: List[str] or None: the aqsids to load
        selected_h3_indices: List[str] or None: the h3 indices to load
        table: str: the table to load the data from
        verbose: bool: print the progress

    Returns:
        pd.DataFrame: the node feature
    """
    assert table in ["hourly_features", "hourly_data"
                     ], "table must be hourly_features or hourly_data"
    assert len(feature) > 0, "features must have at least one feature"
    if table == "hourly_data":
        assert selected_h3_indices is None, "selected_h3_indices can not be provided for hourly_data"

    if verbose:
        print(
            f"[{datetime.now()}] loading node feature {feature} from table {table}"
        )

    # load the node features
    feature_df = pd.DataFrame()
    if verbose:
        print(
            f"[{datetime.now()}] loading features {feature} from table {table}"
        )
    if table == "hourly_features":
        feature_df = load_hourly_feature(
            engine=engine, table_name=table, feature=feature,
            start_time=start_time, end_time=end_time,
            aqsids_filter=selected_aqsids,
            h3_indices_filter=selected_h3_indices, verbose=verbose)
    elif table == "hourly_data":
        feature_df = load_hourly_data(engine=engine, table_name=table,
                                      features=[feature],
                                      start_time=start_time, end_time=end_time,
                                      aqsids_filter=selected_aqsids,
                                      verbose=verbose)
    if verbose:
        print(
            f"[{datetime.now()}] loaded feature {feature} from table {table} with shape {feature_df.shape}"
        )

    return feature_df


def load_node_features(
    engine: "sqlalchemy.engine.Engine",
    start_time: str,
    end_time: str,
    features: List[str],
    selected_aqsids: Union[List[str], None] = None,
    selected_h3_indices: Union[List[str], None] = None,
    table: str = "hourly_features",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load node features from the database.
    
    Load the processed features indexed by aqsids or h3 indices.
    Returns a single dataframes will all features in long
    format.

    Args:
        engine: sqlalchemy.engine.Engine: the database engine
        start_time: str: the start time to load the data for
        end_time: str: the end time to load the data for
        features: List[str]: the features to load
        selected_aqsids: List[str] or None: the aqsids to load
        selected_h3_indices: List[str] or None: the h3 indices to load
        table: str: the table to load the data from
        verbose: bool: print the progress

    Returns:
        pd.DataFrame: the node features
    """
    assert table in ["hourly_features", "hourly_data"
                     ], "table must be hourly_features or hourly_data"
    assert len(features) > 0, "features must have at least one feature"
    if table == "hourly_data":
        assert selected_h3_indices is None, "selected_h3_indices can not be provided for hourly_data"

    if verbose:
        print(f"[{datetime.now()}] loading node features from table {table}")

    # load the node features
    features_df = pd.DataFrame()
    if verbose:
        print(
            f"[{datetime.now()}] loading features {features} from table {table}"
        )
    if table == "hourly_features":
        features_df = load_hourly_features(
            engine=engine, table_name=table, features=features,
            start_time=start_time, end_time=end_time,
            aqsids_filter=selected_aqsids,
            h3_indices_filter=selected_h3_indices, verbose=verbose)
    elif table == "hourly_data":
        features_df = load_hourly_data(engine=engine, table_name=table,
                                       features=features,
                                       start_time=start_time,
                                       end_time=end_time,
                                       aqsids_filter=selected_aqsids,
                                       verbose=verbose)
    if verbose:
        print(
            f"[{datetime.now()}] loaded feature {features} from table {table} with shape {features_df.shape}"
        )

    return features_df
