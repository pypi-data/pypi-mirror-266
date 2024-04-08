import unittest
import tempfile
import torch

from aq_geometric.models.gcn.gcn import GCNModel


class TestAqHierarchicalEdgeConvModel(unittest.TestCase):
    def setUp(self):
        pass

    def test_forward(self):
        model = GCNModel()
        x = torch.randn(10, 5, model.in_channels)
        edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]])
        output = model.forward(x, edge_index)
        self.assertEqual(output.shape, (10, 5, model.out_channels))

    def test_save_and_load(self):
        model = GCNModel()
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = temp_file.name
            model.save(temp_path)

            loaded_model = GCNModel()
            loaded_model.load(temp_path)

        self.assertEqual(model.name, loaded_model.name)
        self.assertEqual(model.guid, loaded_model.guid)
        self.assertEqual(model.stations, loaded_model.stations)
        self.assertEqual(model.features, loaded_model.features)
        self.assertEqual(model.targets, loaded_model.targets)
        self.assertEqual(model.state_dict().keys(), loaded_model.state_dict().keys())

    def test_repr(self):
        model = GCNModel()
        representation = repr(model)
        self.assertIn("GCNModel", representation)
        self.assertIn("Name:", representation)
        self.assertIn("GUID:", representation)
        self.assertIn("Stations:", representation)
        self.assertIn("Features:", representation)
        self.assertIn("Targets:", representation)
    
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
