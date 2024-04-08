import unittest
import tempfile

import torch

from aq_geometric.models.edge_conv.edge_conv import AqEdgeConvModel, EdgeConvModel


class TestEdgeConvModel(unittest.TestCase):
    def setUp(self):
        self.model = EdgeConvModel()

    def test_forward(self):
        # Create dummy input and edge_index tensors
        x = torch.randn(10, self.model.in_channels)
        edge_index = torch.tensor([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])

        # Call the forward method
        output = self.model.forward(x, edge_index)

        # Assert the shape of the output tensor
        self.assertEqual(output.shape, (10, 1))

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = temp_file.name
            self.model.save(temp_path)

            loaded_model = EdgeConvModel()
            loaded_model.load(temp_path)

        self.assertEqual(self.model.name, loaded_model.name)
        self.assertEqual(self.model.guid, loaded_model.guid)
        self.assertEqual(self.model.stations, loaded_model.stations)
        self.assertEqual(self.model.features, loaded_model.features)
        self.assertEqual(self.model.targets, loaded_model.targets)

    def test_init(self):
        # Assert the default values of the model's attributes
        self.assertEqual(self.model.name, "EdgeConvModel")
        self.assertIsInstance(self.model.guid, str)
        self.assertIsNone(self.model.stations)
        self.assertEqual(self.model.features, [])  # none were passed, so it should be empty
        self.assertEqual(self.model.targets, [])  # none were passed, so it should be empty


class TestAqEdgeConvModel(unittest.TestCase):
    def setUp(self):
        self.model = AqEdgeConvModel()

    def test_forward(self):
        # Create dummy input and edge_index tensors
        x = torch.randn(10, self.model.num_samples_in_node_feature * self.model.num_features_in_node_feature)
        edge_index = torch.tensor([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])

        # Call the forward method
        output = self.model.forward(x, edge_index)

        # Assert the shape of the output tensor
        self.assertEqual(output.shape, (10, self.model.out_channels, self.model.num_features_in_node_target))

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = temp_file.name
            self.model.save(temp_path)

            loaded_model = AqEdgeConvModel()
            loaded_model.load(temp_path)

        self.assertEqual(self.model.name, loaded_model.name)
        self.assertEqual(self.model.guid, loaded_model.guid)
        self.assertEqual(self.model.stations, loaded_model.stations)
        self.assertEqual(self.model.features, loaded_model.features)
        self.assertEqual(self.model.targets, loaded_model.targets)

    def test_init(self):
        # Assert the default values of the model's attributes
        self.assertEqual(self.model.name, "AqEdgeConvModel")
        self.assertIsInstance(self.model.guid, str)
        self.assertIsNone(self.model.stations)
        self.assertEqual(self.model.features, ["OZONE", "PM2.5", "NO2"])
        self.assertEqual(self.model.targets, ["OZONE", "PM2.5", "NO2"])
        self.assertEqual(self.model.num_samples_in_node_feature, 48)
        self.assertEqual(self.model.num_samples_in_node_target, 12)
        self.assertEqual(self.model.num_features_in_node_feature, 3)
        self.assertEqual(self.model.num_features_in_node_target, 3)
        self.assertFalse(self.model.verbose)

if __name__ == "__main__":
    unittest.main()