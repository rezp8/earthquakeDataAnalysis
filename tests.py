import unittest
from EMSC_webscraping import webscraping_selenium


class Test(unittest.TestCase):
    def test_validate_selenium_results_count(self):
        events_count, extracted_events_count = webscraping_selenium()
        self.assertEqual(events_count, extracted_events_count,
                         f"Our search included {extracted_events_count} events but only {events_count} have been extracted.")


if __name__ == '__main__':
    unittest.main()
