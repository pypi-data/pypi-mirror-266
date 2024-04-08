import pandas as pd
import unittest

from aq_geometric.utils.station_filters import filter_aqsids


class TestStationFilters(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame for testing
        data = {
            "aqsid": ["AQS1", "AQS2", "AQS3", "AQS4", "AQS5", "AQS4", "AQS5"],
            "value": [100, 200, 300, 400, 500, 600, 700]
        }
        self.df = pd.DataFrame(data)

    def test_filter_aqsids(self):
        # Test with default measurements_cutoff
        selected_stations = filter_aqsids(self.df, measurements_cutoff=0)
        expected_stations = ["AQS5", "AQS4", "AQS3", "AQS2", "AQS1"]
        self.assertEqual(set(selected_stations), set(expected_stations))

        # Test with custom measurements_cutoff
        selected_stations = filter_aqsids(self.df, measurements_cutoff=2)
        expected_stations = ["AQS5", "AQS4"]
        self.assertEqual(set(selected_stations), set(expected_stations))

    def tearDown(self):
        # Clean up any resources used for testing
        pass


if __name__ == "__main__":
    unittest.main()
