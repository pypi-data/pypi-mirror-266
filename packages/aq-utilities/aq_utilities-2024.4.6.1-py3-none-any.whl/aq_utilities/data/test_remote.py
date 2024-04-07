import os
import unittest
from unittest.mock import patch
from aq_utilities.data.remote import download_file
from datetime import datetime


class TestRemoteConfig(unittest.TestCase):

    def test_download_file(self):
        # Mock the urlopen function
        with patch('urllib.request.urlopen') as mock_urlopen:
            # Set up the mock response
            mock_response = mock_urlopen.return_value
            mock_response.read.return_value = b"Test file content"
            
            # Set up the timestamp
            timestamp = datetime(2022, 1, 1)
            
            # Call the function
            result = download_file("http://example.com/test_file.txt", timestamp)
            
            # Assert the expected values
            self.assertEqual(result, ("test_file.txt", "2022/1/1/test_file.txt"))
            mock_urlopen.assert_called_once_with("http://example.com/test_file.txt")
            mock_response.read.assert_called_once()
            
            # Assert that the file was saved to disk
            self.assertTrue(os.path.exists("test_file.txt"))
            with open("test_file.txt", "rb") as f:
                file_content = f.read()
            self.assertEqual(file_content, b"Test file content")
            
            # Clean up the file
            os.remove("test_file.txt")


if __name__ == "__main__":
    unittest.main()