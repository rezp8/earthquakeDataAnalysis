import unittest
from EMSC_webscraping import webscraping_selenium
from GEOFON_webscraping import fetch_earthquake_data
import utils
from io import StringIO
import requests
from API_saving import api_saving
import pandas as pd


class Test(unittest.TestCase):
    def test_selenium_results_count(self):
        total_events_count, extracted_events_count = webscraping_selenium()
        self.assertEqual(total_events_count, extracted_events_count,
                         f"Our search included {extracted_events_count} events but only {total_events_count} have been extracted.")

    def test_beautifulsoup_results_count(self):
        extracted_events_count, total_events_count = fetch_earthquake_data()
        self.assertEqual(total_events_count, extracted_events_count,
                         f"Our search included {extracted_events_count} events but only {total_events_count} have been extracted.")

    def test_validate_api_results_count(self):
        api_saving()

        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "csv",
            "starttime": "2025-09-15",
            "endtime": "2025-10-15",
            "minlatitude": 24,
            "maxlatitude": 46,
            "minlongitude": 123,
            "maxlongitude": 146,
            "minmagnitude": 0
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        df_api = pd.read_csv(StringIO(response.text))
        api_count = len(df_api)

        df_local = pd.read_csv("japan_earthquakes.csv")
        local_count = len(df_local)

        self.assertEqual(
            api_count, local_count,
            f"Our search included {api_count} events but only {local_count} have been extracted.")

    def test_no_missing_values(self):
        df = pd.DataFrame(
            {"data_source": ["EMSC", "EMSC", "EMSC", "EMSC"], "magnitude_value": ["4", "4.5", "2.3", "0"]})
        expected = {"data_source": 0, "magnitude_value": 0}
        result = utils.count_missing_values(df)
        self.assertEqual(result, expected)

    def test_some_missing_values(self):
        df = pd.DataFrame(
            {"data_source": ["EMSC", None, "EMSC", "EMSC"], "magnitude_value": [None, "4.5", None, "0"]})
        expected = {"data_source": 1, "magnitude_value": 2}
        result = utils.count_missing_values(df)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
