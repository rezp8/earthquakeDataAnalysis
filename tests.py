import unittest
from EMSC_webscraping import webscraping_selenium
from GEOFON_webscraping import fetch_earthquake_data
from io import StringIO
import requests
from API_saving import api_saving
import pandas as pd
import numpy as np
from utils import api_code, clean_data, compute_statistics, validate_data_integrity, calculate_distance_to_tokyo, compute_numpy_statistics



class Test(unittest.TestCase):
    def test_selenium_results_count(self):
        total_events_count, extracted_events_count = webscraping_selenium()
        self.assertEqual(total_events_count, extracted_events_count,
                         f"Our search included {extracted_events_count} events but only {total_events_count} have been extracted.")

    def test_beautifulsoup_results_count(self):
        extracted_events_count, total_events_count = fetch_earthquake_data()
        self.assertEqual(total_events_count, extracted_events_count,
                         f"Our search included {extracted_events_count} events but only {total_events_count} have been extracted.")

    def test_api_results_count(self):
        api_saving()
        df_saved = pd.read_csv("JAPAN_USGS.csv")
        saved_count = len(df_saved)
        direct_count = api_code()
        self.assertEqual(saved_count, direct_count,
                         f"Our search included {direct_count} events but only {saved_count} have been extracted.")

    def test_clean_data(self):
        df = pd.DataFrame({
            "latitude": [35.0, np.nan, 37.2],
            "longitude": [138.0, 140.0, np.nan],
            "mag": [4.5, 5.1, np.nan]
        })
        cleaned = clean_data(df)

        self.assertEqual(cleaned.isna().sum().sum(), 0)

    def test_compute_statistics(self):
        df = pd.DataFrame({"magnitude": [4.5, 5.0, 6.0, 7.0]})
        stats = compute_statistics(df, "magnitude")

        self.assertEqual(stats["mean"], 5.625)

    def test_validate_data_integrity(self):
        df = pd.DataFrame({
            "latitude": [35.0, 36.0],
            "longitude": [140.0, 141.0],
            "mag": [5.2, 6.1]
        })
        result = validate_data_integrity(df)

        self.assertTrue(result)

    def test_calculate_distance_to_tokyo(self):
        df = pd.DataFrame({
            "latitude": [35.0, 36.5],
            "longitude": [138.0, 140.0],
            "mag": [4.5, 5.1]
        })
        df_with_dist = calculate_distance_to_tokyo(df)

        self.assertIn("dist_to_tokyo_km", df_with_dist.columns)

    def test_compute_numpy_statistics(self):
        df = pd.DataFrame({
            "latitude": [35.0, 36.5],
            "longitude": [138.0, 140.0],
            "mag": [4.5, 5.1]
        })
        df = calculate_distance_to_tokyo(df)
        stats = compute_numpy_statistics(df)

        self.assertIn("mean_mag", stats)
        self.assertIn("mean_distance", stats)


if __name__ == '__main__':
    unittest.main()
