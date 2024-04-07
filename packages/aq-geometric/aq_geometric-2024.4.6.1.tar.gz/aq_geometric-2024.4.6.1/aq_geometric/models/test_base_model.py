import tempfile
import unittest

from aq_geometric.models.base_model import BaseModel


class TestBaseModel(unittest.TestCase):
    def setUp(self):
        self.model = BaseModel(name="TestModel", guid="12345678-1234-5678-1234-567812345678", stations=["AQS1", "AQS2"])

    def test_save_and_load(self):
        # Create a temporary file path
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_path = temp_file.name

            # Save the model
            self.model.save(temp_path)

            # Load the model
            loaded_model = BaseModel()
            loaded_model.load(temp_path)

            # Check if the loaded model has the same attributes as the original model
            self.assertEqual(self.model.name, loaded_model.name)
            self.assertEqual(self.model.guid, loaded_model.guid)
            self.assertEqual(self.model.stations, loaded_model.stations)

            # Check if the loaded model's state_dict is equal to the original model's state_dict
            self.assertEqual(self.model.state_dict(), loaded_model.state_dict())

    def test_repr(self):
        expected_repr = "BaseModel()\nName: TestModel\nGUID: 12345678-1234-5678-1234-567812345678\nStations: ['AQS1', 'AQS2']\nFeatures: []\nTargets: []"
        self.assertEqual(repr(self.model), expected_repr)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
