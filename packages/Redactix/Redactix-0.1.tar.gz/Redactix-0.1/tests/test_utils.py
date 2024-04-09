# test_utils.py
import sys
import os

# Add the directory containing utils.py to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_package.utils import process_column, modify_csv

import unittest
import pandas as pd
from io import StringIO

class TestUtils(unittest.TestCase):

    def test_process_column(self):
        # Test the processing of a single column with dummy data
        # This is a basic test; adjust with realistic expectations and mock objects as necessary
        texts = ["John Doe", "Jane Smith"]
        processed_texts = process_column(texts)
        self.assertEqual(len(processed_texts), 2)
        # This checks if the processed_texts have been modified, replace with expected behavior
        self.assertNotEqual(processed_texts[0], texts[0])
        self.assertNotEqual(processed_texts[1], texts[1])

    def test_modify_csv(self):
        # Create a dummy CSV for testing
        csv_data = """Ticket ID,Customer Name,Customer Email
1,John Doe,john@example.com
2,Jane Smith,jane@example.com"""
        csv_file = StringIO(csv_data)  # Using StringIO to simulate a file

        # Process the CSV
        processed_df = modify_csv(csv_file)

        # Check if DataFrame is modified correctly
        self.assertIsInstance(processed_df, pd.DataFrame)
        self.assertEqual(len(processed_df.columns), 3)  # Ensure no columns are added or removed
        # These checks ensure that the 'Customer Name' and 'Customer Email' columns are modified
        self.assertNotEqual(processed_df.iloc[0]['Customer Name'], "John Doe")
        self.assertNotEqual(processed_df.iloc[0]['Customer Email'], "john@example.com")

if __name__ == '__main__':
    unittest.main()
