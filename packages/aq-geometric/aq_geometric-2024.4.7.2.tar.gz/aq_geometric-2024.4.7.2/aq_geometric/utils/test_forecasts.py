import unittest
from unittest.mock import MagicMock
from datetime import datetime
import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data

from aq_geometric.models.base_model import BaseModel
from aq_geometric.utils.forecasts import generate_forecasts


class TestGenerateForecasts(unittest.TestCase):
    def setUp(self):
        # Create numpy arrays for node features and targets
        self._num_nodes = 10
        self._num_edges = 20
        self._targets = ["target1", "target2", "target3"]
        self._features = ["feature1", "feature2", "feature3", "feature4", "feature5"]

        self._num_node_features = len(self._features)
        self._num_node_targets = len(self._targets)
        self._num_samples_in_node_feature = 10
        self._num_samples_in_node_target = 5
        self._num_edge_attrs = 2
        self._feature_timestamps = pd.date_range(start="2021-01-01", periods=self._num_samples_in_node_feature, freq="H").to_numpy()
        self._target_timestamps = pd.date_range(start="2021-01-01 10:00:00", periods=self._num_samples_in_node_target, freq="H").to_numpy()

        node_features = torch.rand(self._num_nodes, self._num_samples_in_node_feature, self._num_node_features)
        node_targets = torch.rand(self._num_nodes, self._num_samples_in_node_target, self._num_node_targets)
        pred = torch.rand(self._num_nodes, self._num_samples_in_node_target, self._num_node_targets)
        pred_flat = torch.rand(self._num_nodes, self._num_samples_in_node_target*self._num_node_targets).reshape(-1)

        edges = torch.randint(0, self._num_nodes, (2, self._num_edges))
        edge_features = torch.rand(self._num_edges, self._num_edge_attrs)
        h3_index = np.random.randint(0, 100, (self._num_nodes,))
        aqsid = np.random.randint(0, 100, (self._num_nodes,))
        x_mask = torch.randint(0, 2, (self._num_nodes, self._num_samples_in_node_feature, self._num_node_features))
        y_mask = torch.randint(0, 2, (self._num_nodes, self._num_samples_in_node_target, self._num_node_targets))
        
        feature_start_time = datetime.now()
        feature_end_time = datetime.now()
        target_start_time = datetime.now()
        target_end_time = datetime.now()

        # Create a sample graph for testing
        graph = Data(
                    x=node_features,
                    y=node_targets,
                    edge_index=edges,
                    edge_attr=edge_features,
                    h3_index=h3_index,
                    aqsid=aqsid,
                    x_mask=x_mask,
                    y_mask=y_mask,
                    feature_start_time=feature_start_time,
                    feature_end_time=feature_end_time,
                    feature_timestamps=self._feature_timestamps,
                    target_timestamps=self._target_timestamps,
                    target_start_time=target_start_time,
                    target_end_time=target_end_time,
                    feature_names=self._features,
                    target_names=self._targets,
                )
        self.graph = graph
        self.pred = pred
        self.pred_flat = pred_flat

    def test_generate_forecasts(self):
        # Create a mock model
        model = MagicMock(spec=BaseModel)
        model.name = "TestModel"
        model.num_samples_in_node_feature = self._num_samples_in_node_feature
        model.num_samples_in_node_target = self._num_samples_in_node_target
        model.return_value = self.pred

        # Create a mock dataset
        dataset = MagicMock()
        dataset.get.return_value = self.graph

        # Call the generate_forecasts function
        result = generate_forecasts(model, dataset, include_history=True, verbose=True)

        # Assert the result is a dictionary
        self.assertIsInstance(result, dict)

        # Assert the result contains the expected keys
        expected_keys = ["target1", "target2", "target3"]
        self.assertCountEqual(result.keys(), expected_keys)

        # Assert the result values are pandas DataFrames
        for value in result.values():
            self.assertIsInstance(value, pd.DataFrame)

        # Assert the the DataFrames have the expected shape
        for value in result.values():
            self.assertEqual(value.shape, (self._num_nodes, self._num_samples_in_node_target + self._num_samples_in_node_feature))
        
        # Assert that we have one frame per target
        self.assertEqual(len(result), len(self._targets))

        # Call the generate_forecasts function without history
        result = generate_forecasts(model, dataset, include_history=False, verbose=True)

        # Assert the result is a dictionary
        self.assertIsInstance(result, dict)

        # Assert the result contains the expected keys
        expected_keys = ["target1", "target2", "target3"]
        self.assertCountEqual(result.keys(), expected_keys)

        # Assert the result values are pandas DataFrames
        for value in result.values():
            self.assertIsInstance(value, pd.DataFrame)

        # Assert the the DataFrames have the expected shape
        for value in result.values():
            self.assertEqual(value.shape, (self._num_nodes, self._num_samples_in_node_target))
        
        # Assert that we have one frame per target
        self.assertEqual(len(result), len(self._targets))


if __name__ == "__main__":
    unittest.main()
