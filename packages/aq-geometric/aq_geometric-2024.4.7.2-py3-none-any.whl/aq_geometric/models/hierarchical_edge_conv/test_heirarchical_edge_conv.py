import unittest
import tempfile
from unittest.mock import patch
import torch

from aq_geometric.models.hierarchical_edge_conv.heirarchical_edge_conv import AqHierarchicalEdgeConvModel


class TestAqHierarchicalEdgeConvModel(unittest.TestCase):
    def setUp(self):
        # Create some dummy data for testing
        self.edges_low_to_high_resolution = {1: torch.tensor([[0, 1], [1, 2]]), 2: torch.tensor([[0, 2], [1, 3]])}
        self.edges_high_to_low_resolution = {1: torch.tensor([[0, 1], [1, 2]]), 2: torch.tensor([[0, 2], [1, 3]])}

    def test_forward(self):
        model = AqHierarchicalEdgeConvModel(
            edges_low_to_high_resolution=self.edges_low_to_high_resolution,
            edges_high_to_low_resolution=self.edges_high_to_low_resolution,
            finest_resolution=2,
            coarsest_resolution=1,
        )
        x = torch.randn(10, model.hidden_channels, model.num_features_in_node_feature)
        edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]])
        output = model.forward(x, edge_index)
        self.assertEqual(output.shape, (10*model.num_features_in_node_target, model.out_channels))

    def test_save_and_load(self):
        model = AqHierarchicalEdgeConvModel(
            edges_low_to_high_resolution=self.edges_low_to_high_resolution,
            edges_high_to_low_resolution=self.edges_high_to_low_resolution,
            finest_resolution=2,
            coarsest_resolution=1,
        )
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = temp_file.name
            model.save(temp_path)

            loaded_model = AqHierarchicalEdgeConvModel()
            loaded_model.load(temp_path)

        self.assertEqual(model.name, loaded_model.name)
        self.assertEqual(model.guid, loaded_model.guid)
        self.assertEqual(model.stations, loaded_model.stations)
        self.assertEqual(model.features, loaded_model.features)
        self.assertEqual(model.targets, loaded_model.targets)
        self.assertEqual(model.num_samples_in_node_feature, loaded_model.num_samples_in_node_feature)
        self.assertEqual(model.num_samples_in_node_target, loaded_model.num_samples_in_node_target)
        self.assertEqual(model.finest_resolution, loaded_model.finest_resolution)
        self.assertEqual(model.coarsest_resolution, loaded_model.coarsest_resolution)
        self.assertEqual(model.cheb_k, loaded_model.cheb_k)
        self.assertEqual(model.state_dict().keys(), loaded_model.state_dict().keys())

    def test_repr(self):
        model = AqHierarchicalEdgeConvModel(
            edges_low_to_high_resolution=self.edges_low_to_high_resolution,
            edges_high_to_low_resolution=self.edges_high_to_low_resolution,
            finest_resolution=2,
            coarsest_resolution=1,
        )
        representation = repr(model)
        self.assertIn("AqHierarchicalEdgeConvModel", representation)
        self.assertIn("Name:", representation)
        self.assertIn("GUID:", representation)
        self.assertIn("Stations:", representation)
        self.assertIn("Features:", representation)
        self.assertIn("Targets:", representation)
        self.assertIn("Samples in Node Features:", representation)
        self.assertIn("Samples in Node Targets:", representation)
    
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
