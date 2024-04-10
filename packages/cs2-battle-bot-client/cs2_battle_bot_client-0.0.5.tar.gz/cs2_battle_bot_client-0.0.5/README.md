
# CS2 Battle Bot Client

## Description

This is a Python client for the CS2 Battle Bot API. It uses the OpenAPI Python Generator for API interactions and Pydantic for data modeling.

## Installation

### With pip
1. Install the package using pip:
```shell
pip install cs2-battle-bot-client
```
### With poetry
1. Install the package using poetry:
```shell
poetry add cs2-battle-bot-client
```

## Usage
1. Set `access_token` environment variable to the access token you received from the CS2 Battle Bot API.
```shell
export access_token="your_access_token"
```
2. Use the client in your Python code:
```python
from cs2_battle_bot_client import APIConfig
from cs2_battle_bot_client.services import matches_service

api_config = APIConfig(
    base_url="http://localhost:8000"
)

def main():
    matches = matches_service.matches_list(api_config_override=api_config)
    print(matches)
    
if __name__ == "__main__":
    main()

```