from datetime import datetime
from typing import List, Union

import numpy as np
import pandas as pd


def ensure_feature_axis(df: pd.DataFrame, h3_indices: List[str],
                        missing_value: Union[int, float] = np.nan,
                        verbose: bool = False) -> pd.DataFrame:
    """Ensure the return from remote has the correct columns and rows."""
    # ensure the columns are correct
    if verbose:
        print(
            f"[{datetime.now()}] dropping any columns that are not h3 indices (current shape: {df.shape})"
        )
    # drop any columns that are not in the list of requested h3 indices
    h3_indices_in_df = set(df.columns)
    h3_indices = set(h3_indices)
    h3_indices_in_df = list(h3_indices.intersection(h3_indices_in_df))
    df = df[h3_indices_in_df]
    if verbose:
        print(
            f"[{datetime.now()}] dropped any columns that are not h3 indices (current shape: {df.shape})"
        )
    # add new columns ful of nans for any missing h3 indices
    missing_h3_indices = list(set(h3_indices) - set(h3_indices_in_df))
    if verbose:
        print(
            f"[{datetime.now()}] adding {len(missing_h3_indices)} columns for missing h3 indices (current shape: {df.shape})"
        )
    for h3_index in missing_h3_indices:
        df[h3_index] = missing_value
    if verbose:
        print(f"[{datetime.now()}] returning with shape {df.shape}")
    return df
