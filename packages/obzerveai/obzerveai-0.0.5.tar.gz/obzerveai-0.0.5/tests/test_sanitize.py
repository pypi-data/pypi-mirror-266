import unittest
from unittest.mock import patch, MagicMock
from src.obzerveai.sanitize import ObzerveAI  # Assuming the class is in a file named obzerve_ai.py

class TestObzerveAI(unittest.TestCase):

    def setUp(self):
        # Set up your test case with any necessary default values
        self.default_token = 'default_token'
        self.default_org = 'default_org'
        self.default_bucket = 'default_bucket'
        self.default_url = 'http://localhost:9999'
        self.obzerve_ai = ObzerveAI(self.default_token, self.default_org, self.default_bucket, self.default_url)

    def test_init_with_default_values(self):
        # Test initialization with default values
        self.assertEqual(self.obzerve_ai.token, self.default_token)
        self.assertEqual(self.obzerve_ai.org, self.default_org)
        self.assertEqual(self.obzerve_ai.bucket, self.default_bucket)
        self.assertEqual(self.obzerve_ai.url, self.default_url)

    @patch('src.obzerveai.sanitize.InfluxDBClient')
    def test_influxdb_connection_success(self, mock_influxdb_client):
        # Test successful connection to InfluxDB
        mock_influxdb_client.return_value = MagicMock()
        try:
            ObzerveAI(self.default_token, self.default_org, self.default_bucket, self.default_url)
        except Exception as e:
            self.fail(f"Initialization failed with an exception: {e}")

    @patch('src.obzerveai.sanitize.InfluxDBClient')
    def test_influxdb_connection_failure(self, mock_influxdb_client):
        # Test InfluxDB connection failure
        mock_influxdb_client.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception) as context:
            ObzerveAI(self.default_token, self.default_org, self.default_bucket, 'http://invalid_url:9999')
        self.assertTrue('Connection failed' in str(context.exception))

    # TODO: Fix this test case
    # @patch('src.obzerveai.sanitize.InfluxDBClient')
    # def test_track_usage_successful_write(self, mock_influxdb_client):
    #     # Test successful write to InfluxDB
    #     mock_write = MagicMock()
    #     mock_write_api = MagicMock()
    #     mock_write_api.write.return_value = mock_write
    #     mock_influxdb_client.write_api.return_value = mock_write_api
    #     self.obzerve_ai.track_usage()
    #     mock_write.assert_called_once()

    def test_redact_sensitive_info_email(self):
        # Test redaction of email addresses
        test_string = "Contact me at test@example.com"
        redacted_string = self.obzerve_ai.redact_sensitive_info(test_string)
        self.assertEqual(redacted_string, "Contact me at [REDACTED - emails]")

    # Additional test cases for redact_sensitive_info would follow the same pattern as above

    @patch.object(ObzerveAI, 'track_usage')
    def test_redact_sensitive_info_invokes_track_usage(self, mock_track_usage):
        # Test that track_usage is called when redact_sensitive_info is invoked
        test_string = "Contact me at test@example.com"
        self.obzerve_ai.redact_sensitive_info(test_string)
        mock_track_usage.assert_called_once()

if __name__ == '__main__':
    unittest.main()