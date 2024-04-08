import os
import unittest
from unittest.mock import patch
from datetime import datetime
from aq_utilities.engine.psql import get_engine
from aq_utilities.data.psql import get_max_timestamp, get_min_timestamp


class TestPsql(unittest.TestCase):
    @patch.dict(
        os.environ, {
            "PGUSER": "pgadmin",
            "PGPASSWORD": "test_password",
            "PGHOST": "test_host",
            "PGDATABASE": "test_db",
            "PGPORT": "5432"
        })
    def test_get_max_timestamp(self):
        # Set up the test data
        table_name = "test_table"
        timestamp_col_name = "timestamp"
        expected_timestamp = datetime(2022, 1, 1, 0, 0, 0)

        # Mock the engine
        engine = get_engine()

        # Mock the connection and result
        with patch.object(engine, "connect") as mock_connect:
            mock_connection = mock_connect.return_value.__enter__.return_value
            mock_result = mock_connection.execute.return_value
            mock_result.__iter__.return_value = [[expected_timestamp]]

            # Call the function
            result = get_max_timestamp(table_name, timestamp_col_name, engine)

            # Assert the result
            self.assertEqual(result, expected_timestamp)

    def test_get_min_timestamp(self):
        # Set up the test data
        table_name = "test_table"
        timestamp_col_name = "timestamp"
        expected_timestamp = datetime(2021, 1, 1, 0, 0, 0)

        # Mock the engine
        engine = get_engine()

        # Mock the connection and result
        with patch.object(engine, "connect") as mock_connect:
            mock_connection = mock_connect.return_value.__enter__.return_value
            mock_result = mock_connection.execute.return_value
            mock_result.__iter__.return_value = [[expected_timestamp]]

            # Call the function
            result = get_min_timestamp(table_name, timestamp_col_name, engine)

            # Assert the result
            self.assertEqual(result, expected_timestamp)

if __name__ == "__main__":
    unittest.main()