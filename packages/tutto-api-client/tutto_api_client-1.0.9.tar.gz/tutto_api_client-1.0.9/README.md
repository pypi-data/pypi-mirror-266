# Tutto API Client
Tutto API Client is a Python client for the Tutto API. It provides a simple and pythonic way to interact with the Tutto API.

## Advantages
- **Simple**: Tutto API Client is designed to be simple and easy to use.
- **Complete**: Tutto API Client is designed to be complete and provides all the features of the Tutto API.
- **High Performance**: Tutto API Client is designed to be high performance due to its asynchronous nature when making HTTP requests to Tutto API.
- **Lightweight**: Tutto API Client is designed to be lightweight and has only 2 dependencies.
    > aiohttp **and** aiodns

## Installation
```bash
pip install tutto-api-client
```

## Usage
```python
from tutto_api_client import TuttoAPIClient, Authorization

base_url = "https://my.tutto.base.url/tuttoapi/"

# Create Authorization object and TuttoAPIClient
auth = Authorization(
    base_url=base_url,
    user="a_user",
    password="a_password",
    basic_auth_token="a_big_token",
    user_type="external",
)
client = TuttoAPIClient(base_url=base_url, authorization=auth)

# Get an endpoint and print the response dict
deductions_endpoint = client.get_deductions(reference="202401")
endpoint_response = deductions_endpoint.call()
print(endpoint_response)
```