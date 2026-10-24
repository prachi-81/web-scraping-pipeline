
import unittest
from scraper import generate_report


class ScraperTests(unittest.TestCase):
    def test_empty_records_report(self):
        generate_report([])

    def test_report_with_records(self):
        records = [
            {"quote": "Example one", "author": "Author A", "tags": "test"},
            {"quote": "Example two", "author": "Author A", "tags": "demo"},
        ]
        generate_report(records)


if __name__ == "__main__":
    unittest.main()
