from datetime import datetime

import pandas as pd


def load_hourly_data_from_fp(
    fp: str = "hourly_data.csv",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    df = pd.read_csv(fp)

    assert "aqsid" in df.columns, "aqsid must be in the dataframe"  # aqsid is the station id
    assert "timestamp" in df.columns, "timestamp must be in the dataframe"
    assert "value" in df.columns, "value must be in the dataframe"
    assert "measurement" in df.columns, "measurement must be in the dataframe"

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["aqsid"] = df["aqsid"].astype(str)

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_stations_info_from_fp(
    fp: str = "stations_info.csv",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    df = pd.read_csv(fp)

    assert "aqsid" in df.columns, "aqsid must be in the dataframe"  # aqsid is the station id
    assert "longitude" in df.columns, "longitude must be in the dataframe"
    assert "latitude" in df.columns, "latitude must be in the dataframe"

    df["aqsid"] = df["aqsid"].astype(str)

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_hourly_features_from_fp(
    fp: str = "hourly_features.csv",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    df = pd.read_csv(fp)

    assert "aqsid" in df.columns, "aqsid must be in the dataframe"  # aqsid is the station id
    assert "h3_index" in df.columns, "h3_index must be in the dataframe"
    assert "timestamp" in df.columns, "timestamp must be in the dataframe"
    assert "value" in df.columns, "value must be in the dataframe"
    assert "measurement" in df.columns, "measurement must be in the dataframe"

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["aqsid"] = df["aqsid"].astype(str)
    df["h3_index"] = df["h3_index"].astype(str)

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_hourly_feature_from_fp(
    fp: str = "hourly_feature.csv",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    df = pd.read_csv(fp)

    assert "h3_index" in df.columns, "h3_index must be in the dataframe"
    assert "timestamp" in df.columns, "timestamp must be in the dataframe"
    assert "value" in df.columns, "value must be in the dataframe"

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["h3_index"] = df["h3_index"].astype(str)

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def save_hourly_data_to_fp(
    df: pd.DataFrame,
    fp: str = "hourly_data.csv",
    verbose: bool = False,
) -> None:
    """Save the dataframe to disk."""
    df.to_csv(fp, index=False)

    if verbose: print(f"[{datetime.now()}] saved hourly_data to: {fp}")


def save_stations_info_to_fp(
    df: pd.DataFrame,
    fp: str = "stations_info.csv",
    verbose: bool = False,
) -> None:
    """Save the dataframe to disk."""
    df.to_csv(fp, index=False)

    if verbose: print(f"[{datetime.now()}] saved stations_info to: {fp}")


def save_hourly_features_to_fp(
    df: pd.DataFrame,
    fp: str = "hourly_features.csv",
    verbose: bool = False,
) -> None:
    """Save the dataframe to disk."""
    df.to_csv(fp, index=False)

    if verbose: print(f"[{datetime.now()}] saved hourly_features to: {fp}")
