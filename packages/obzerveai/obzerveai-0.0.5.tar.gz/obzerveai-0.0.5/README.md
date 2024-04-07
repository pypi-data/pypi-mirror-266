# ObzerveAI
ObzerveAI is a middleware for your AI applications and models. It provides a simple interface for redacting sensitive information from your prompts. It also helps you to monitor and visualize the usage metrics.
## Features
- Redaction of sensitive information from your prompts.
- Monitoring of function usage with metrics recorded in InfluxDB.
- Visualization of the metrcs using grafana
## Installation
### Setup InfluxDB and Grafana
Using docker compose you can setup influxdb and grafana with default configurations and sample dashboard. After cloning the repo, run the following command
```bash
docker-compose up -d
```
This will setup a grafana at http://localhost:3000 and influxdb on http://localhost:8086
### Python Package
To install the package run following command
```bash
pip install obzerveai
```
## Usage
To use ObzerveAI, you need to create an instance of the ObzerveAI class and then call the redact_sensitive_info method with the text you want to sanitize.
```python
from obzerve_ai import ObzerveAI

# Initialize the ObzerveAI instance with default or custom parameters
obzerve_ai = ObzerveAI()

# Redact sensitive information from text
sensitive_text = "Contact me at example@example.com or call me at 123-456-7890."
redacted_text = obzerve_ai.redact_sensitive_info(sensitive_text)

print(redacted_text)
```
## Dashboard
A pre-created dashboard will be available. You can access it at http://localhost:3000/dashboards
![image](https://raw.githubusercontent.com/obzerveai/obzerveai/main/images/dashboard.png)
## Advanced Configuration
You can choose to change the influxdB configurations with the following parameters while initiating the ObzerveAI class:
```python
obzerve_ai = ObzerveAI(token="your_influxdb_token", org="your_org", bucket="your_bucket", url="your_influxdb_url")
```
- `token`: InfluxDB authentication token (default: "my_default_token_value").
- `org`: InfluxDB organization name (default: "obzerve_ai").
- `bucket`: InfluxDB bucket name where usage data will be stored (default: "usage").
- `url`: URL of the InfluxDB instance (default: "http://localhost:8086").
