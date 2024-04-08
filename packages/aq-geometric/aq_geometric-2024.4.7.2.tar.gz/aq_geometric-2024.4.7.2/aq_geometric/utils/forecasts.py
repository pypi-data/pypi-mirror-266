from datetime import datetime
from typing import Dict, Union, List

import torch
import numpy as np
import pandas as pd
from aq_utilities.data import hourly_predictions_to_postgres


def generate_forecasts_graph(
    model: "aq_geometric.models.base_model.BaseModel",
    dataset: "AqGeometricInMemoryDataset",
    targets: List[str],
    include_history: bool = False,
    verbose: bool = False,
) -> Dict[str, pd.DataFrame]:
    """
    Generate forecasts using the model provided
    """
    forecasts = []

    # obtain data attributes
    if verbose:
        print(f"[{datetime.now()}] reading from dataset")
    g = dataset.get(0)
    inputs = g.x
    input_edge_index = g.edge_index
    h3_indices = g.h3_index
    aqsids = g.aqsid
    timestamps = g.timestamps
    feature_timestamps = g.feature_timestamps
    target_timestamps = g.target_timestamps

    with torch.no_grad():
        if verbose:
            print(f"[{datetime.now()}] generating forecasts for {len(h3_indices)} h3 indices")
        pred = model(inputs, input_edge_index)
        # reshape the prediction to the shape of the target
        pred = pred.numpy().reshape(g.y_mask.shape)
    
    # prepare the forecasts, including the history
    target_dfs = {}
    history = g.x.detach().numpy()
    testmask = g.x_mask[:, 0, :].numpy()
    forecasts = (testmask.reshape(-1, 1, len(targets)) * pred)

    for i, target in enumerate(targets):
        if verbose:
            print(f"[{datetime.now()}] preparing forecast for {target}")
        history_df = pd.DataFrame(
            history[:,:,i], columns=feature_timestamps, index=h3_indices
        ) if include_history else pd.DataFrame()
        if verbose:
            print(f"[{datetime.now()}] history df shape for {target}: {history_df.shape}")
        forecast_df = pd.DataFrame(
            forecasts[:,:,i], columns=target_timestamps, index=h3_indices
        )
        if verbose:
            print(f"[{datetime.now()}] forecast df shape for {target}: {forecast_df.shape}")
        df = pd.concat([history_df, forecast_df], axis=1)
        target_dfs[target] = df
        if verbose:
            print(f"[{datetime.now()}] added DataFrame {df.shape}")

    return target_dfs, g


def forecasts_df_to_db(
    engine: str,
    model: "aq_geometric.models.base_model.BaseModel",
    graph: "Data",
    target_dfs: Dict[str, pd.DataFrame],
    run_id: Union[str, None] = None,
    chunksize: int = 1000,
    continue_on_error: bool = False,
    verbose: bool = False,
) -> int:
    """
    Write the forecasts to the database
    """
    # generate a random run id if none is provided
    if run_id is None:
        import uuid
        run_id = str(uuid.uuid4())

    # obtain model attributes
    model_id = model.guid
    model_name = model.name

    for target, forecast_df in target_dfs.items():
        if verbose:
            print(f"[{datetime.now()}] writing forecast for {target} to database")
        # read from the graph used to generate forecasts
        assert len(graph.h3_index) == len(graph.aqsid)
        df = pd.DataFrame(np.stack((graph.h3_index.T, graph.aqsid.T), axis=1), columns=["h3_index", "aqsid"])

        # obtain the timestamps
        timestamps = forecast_df.columns.to_list()
        data = forecast_df.values
        max_timestamp_in_samples = graph.feature_end_time
        predicted_at_timestamp = pd.Timestamp.now()

        # prepare the data
        for i, timestamp in enumerate(timestamps):
            df["value"] = data[:, i]
            df["timestamp"] = timestamp
            df["predicted_at_timestamp"] = predicted_at_timestamp
            df["max_timestamp_in_samples"] = max_timestamp_in_samples
            df["model_id"] = model_id
            df["model_name"] = model_name
            df["run_id"] = run_id
            df["measurement"] = target

            # write the predictions to postgres
            err = hourly_predictions_to_postgres(
                predictions=df,
                engine=engine,
                chunksize=chunksize,
            )
            if err == 1:
                print(f"failed to write predictions to postgres: {err}")
                if continue_on_error: continue
                else: return 1

    return 0


def forecasts_graph_to_json(
    model: "aq_geometric.models.base_model.BaseModel",
    graph: "Data",
    targets: List[str],
    target_dfs: Dict[str, pd.DataFrame],
    verbose: bool = False,
) -> dict:
    """Prepare the forecast in json format"""
    # generate the frontend data
    fe_data = {}
    fe_data["num_history_samples"] = model.num_samples_in_node_feature
    fe_data["num_forecast_samples"] = model.num_samples_in_node_target
    model_name = model.name
    
    # we also want to include the history and the forecasts
    fe_data[model_name] = {
        **{target_name: {} for target_name in targets},
    }
    timestamps = None
    history_and_forecasts_len = -1
    for target_name, forecast_df in target_dfs.items():
        if verbose:
            print(f"[{datetime.now()}] preparing forecast for {target_name}")
        if timestamps is None:
            timestamps = forecast_df.columns.to_list()
        for row_ in forecast_df.iterrows():
            h3_index = row_[0]
            fe_data[model_name][target_name][h3_index] = [int(v) for v in row_[1].fillna(0).tolist()]
            if history_and_forecasts_len == -1:
                history_and_forecasts_len = len(row_[1])
            else:
                if history_and_forecasts_len != len(row_[1]):
                    raise ValueError("forecast lengths do not match")
    
    # if we did not include history, we still want to include the timestamps'
    if history_and_forecasts_len == model.num_samples_in_node_target:
        fe_data["num_history_samples"] = 0
        if verbose:
            print(f"[{datetime.now()}] no history included in forecast")

    # we want access to the timestamps when displaying the data
    fe_data["timestamps"] = [
        str(t) for t in timestamps
    ]

    if verbose:
        print(f"[{datetime.now()}] frontend datetimes: [{fe_data['timestamps'][0]}, {fe_data['timestamps'][-1]}]")
        print(f"[{datetime.now()}] prepared forecast for frontend")

    return fe_data
