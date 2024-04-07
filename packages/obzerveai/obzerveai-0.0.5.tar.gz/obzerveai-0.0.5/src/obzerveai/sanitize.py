from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import re


class ObzerveAI:
    def __init__(
        self,
        token="my_default_token_value",
        org="obzerve_ai",
        bucket="usage",
        url="http://localhost:8086",
    ):
        self.token = token
        self.org = org
        self.bucket = bucket
        self.url = url
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.client.ping()  # Check if InfluxDB is available
        except Exception as e:
            raise ConnectionError(
                "ObzerveAI: Failed to connect to InfluxDB: {}".format(e)
            )

    def track_usage(self):
        try:
            write_api = self.client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("function_usage")
                .tag("function", "redact_sensitive_info")
                .field("value", 1)
            )
            write_api.write(bucket=self.bucket, record=point)
        except Exception as e:
            print("ObzerveAI: Failed to write to InfluxDB: {}".format(e))

    def redact_sensitive_info(self, text):
        # Regular expressions for sensitive information
        regex_patterns = {
            # 'names': r'\b[A-Z][a-z]+\b(?:\s[A-Z][a-z]+)*',
            # 'addresses': r'\d{1,5}\s\w+\s\w+\s\w+|\d{1,5}\s\w+\s\w+',
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone_numbers": r"\b(?:\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{3}[-.\s]??\d{4})\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "passport": r"^[a-zA-Z]{1}\d{8}$",
            "drivers_license": r"^[a-zA-Z]{1}\d{7}$",
            "date": r"\d(3[01]|[12][0-9]|0?[1-9])(\/|-)(1[0-2]|0?[1-9])\2([0-9]{2})?[0-9]{2}",
            "credit_cards": r"^\d{4}-\d{4}-\d{4}-\d{4}$",
            "health_info": r"\b\d{3}-\d{2}-\d{4}\b",  # Sample for medical record numbers
            # 'financial_info': r'\b(?:\d[ -]*?){13,16}\b'  # Sample for credit card or account numbers
        }

        redacted_text = text
        for category, pattern in regex_patterns.items():
            # if type(pattern) == list:
            #     for each_pattern in pattern:
            #         print(each_pattern)
            #         redacted_text = re.sub(each_pattern, '[REDACTED - {}]'.format(category), redacted_text)
            # else:
            redacted_text = re.sub(
                pattern, "[REDACTED - {}]".format(category), redacted_text
            )

        self.track_usage()
        return redacted_text


# Example usage:
if __name__ == "__main__":
    obzerve_ai = ObzerveAI()  # You can pass custom values if needed
    sensitive_text = "Contact me at example@example.com or call me at 123-456-7890."
    redacted_text = obzerve_ai.redact_sensitive_info(sensitive_text)
    print(redacted_text)
