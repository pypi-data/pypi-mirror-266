import unittest
import pandas as pd
from scalexi.document_loaders.context_loaders import context_from_csv_as_series, context_from_csv_as_df
import os

class TestContextFromCSV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This CSV is for testing purposes
        cls.test_csv_path = 'test.csv'
        cls.test_data = {
            'context': ["Sample context 1", "Sample context 2", "Sample context 3"],
            'other_column': [1, 2, 3]
        }
        # Create a test CSV file
        pd.DataFrame(cls.test_data).to_csv(cls.test_csv_path, index=False)

    @classmethod
    def tearDownClass(cls):
        # Remove the test CSV file after tests
        os.remove(cls.test_csv_path)

    def test_context_from_csv_as_series(self):
        # Test if the function returns the correct pandas Series
        result_series = context_from_csv_as_series(self.test_csv_path)
        expected_series = pd.Series(self.test_data['context'], name='context')
        pd.testing.assert_series_equal(result_series, expected_series)

    def test_context_from_csv_as_df(self):
        # Test if the function returns the correct pandas DataFrame
        result_df = context_from_csv_as_df(self.test_csv_path)
        expected_df = pd.DataFrame(self.test_data['context'], columns=['context'])
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_file_not_found_error(self):
        # Test if FileNotFoundError is raised when file does not exist
        with self.assertRaises(FileNotFoundError):
            context_from_csv_as_series('non_existent_file.csv')

    def test_column_not_found_error(self):
        # Test if ValueError is raised when column does not exist
        with self.assertRaises(ValueError):
            context_from_csv_as_series(self.test_csv_path, 'non_existent_column')

# Replace 'your_module_name' with the actual name of your module
if __name__ == '__main__':
    unittest.main()
