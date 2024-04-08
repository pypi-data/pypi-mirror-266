from datetime import datetime

import pandas as pd


def filter_features_by_measurement(
    features_df: pd.DataFrame,
    measurement: str,
    verbose: bool = False,
) -> pd.DataFrame:
    """Filter the dataframe by measurement."""
    assert "measurement" in features_df.columns, "measurement must be in the dataframe"

    if verbose:
        print(f"[{datetime.now()}] filtering by measurement: {measurement}")
    features_df = features_df[features_df["measurement"] == measurement]
    if verbose:
        print(
            f"[{datetime.now()}] after filtering dataframe has shape: {features_df.shape}"
        )
    return features_df


def filter_features_by_h3_indices(
    features_df: pd.DataFrame,
    h3_indices: str,
    verbose: bool = False,
) -> pd.DataFrame:
    """Filter the dataframe by measurement."""
    if verbose:
        print(f"[{datetime.now()}] filtering by h3_indices: {h3_indices}")
    features_df = features_df[features_df["h3_inbdex"].isin(h3_indices)]
    if verbose:
        print(
            f"[{datetime.now()}] after filtering dataframe has shape: {features_df.shape}"
        )
    return features_df
