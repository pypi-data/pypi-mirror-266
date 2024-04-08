import numpy as np
import unittest

from aq_geometric.utils.evaluation import evaluate_graph_predictions


class TestEvaluation(unittest.TestCase):
    def test_evaluate_graph_predictions(self):
        pred = np.array([1, 2, 3, 4, 5])
        true = np.array([1, 2, 3, 4, 5])
        num_stations = 3

        expected_metrics = {
            "station_level": {
                "mae": 0,
                "rmse":0,
                "mape": 0,
                "r2": 1
            },
            "index_level": {
                "mae": 0,
                "rmse": 0,
                "mape": 0,
                "r2": 1
            }
        }

        metrics = evaluate_graph_predictions(pred, true, num_stations)

        self.assertEqual(metrics, expected_metrics)

if __name__ == '__main__':
    unittest.main()
