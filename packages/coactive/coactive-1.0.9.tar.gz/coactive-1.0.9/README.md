# Coactive Python Library

[![pypi](https://img.shields.io/pypi/v/fern-coactive.svg)](https://pypi.python.org/pypi/coactive)
[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://buildwithfern.com/?utm_source=coactiveai/coactive-python/readme)


## Documentation

API Documentation can be found [here](https://docs.coactive.ai/)

## Installation

Add this dependency to your project's build file:

```bash
pip install coactive
# or
poetry add coactive
```

## Usage

```python
from coactive.client import Coactive
from coactive import StorageTypeEnum

coactive_client = Coactive(
  client_id="YOUR_CLIENT_ID",
  client_secret="YOUR_CLIENT_SECRET",
)

dataset = coactive_client.dataset.create(
  name = "visual_data",
  description = "A dataset containing images and videos.",
  storage_type = StorageTypeEnum.S3,
  data_path="s3://coactive-demo-datasets/quickstart/",
)

print(f"Created dataset with id {dataset.dataset_id}");
```

## Async Client

```python
from coactive.client import AsyncCoactive
from coactive import StorageTypeEnum

import asyncio

coactive_client = AsyncCoactive(
  client_id="YOUR_CLIENT_ID",
  client_secret="YOUR_CLIENT_SECRET",
)

async def create_dataset() -> None:
    dataset = coactive_client.dataset.create(
      name = "visual_data",
      description = "A dataset containing images and videos.",
      storage_type = StorageTypeEnum.S3,
      data_path="s3://coactive-demo-datasets/quickstart/",
    )
    print(f"Created dataset with id {dataset.dataset_id}");

asyncio.run(create_dataset())
```

## Timeouts
By default, the client is configured to have a timeout of 60 seconds. 
You can customize this value at client instantiation. 

```python
from coactive.client import Coactive

coactive_client = AsyncCoactive(
  client_id="YOUR_CLIENT_ID",
  client_secret="YOUR_CLIENT_SECRET",
  timeout=30 # timeout is set to 30 seconds
)
```

## Handling Exceptions
All exceptions thrown by the SDK will sublcass [coactive.ApiError](./src/coactive/core/api_error.py). 

```python
from coactive.core import APIError
import coactive

try:
  flatfile_client.environments.get(id="environment-id")
except coactive.NotFoundError as e: 
  # handle bad request error
except APIError as e:  
  # handle any api related error
```

Error codes are as followed:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `UnauthorizedError`        |
| 403         | `ForbiddenError`           |
| 404         | `NotFoundError`            |
| 429         | `UnprocessableEntityError` |

## Custom Base URL
By default the client will send requests to `https://app.coactive.ai`. 
You can point the client at a different domain by populating
the `base_url` field: 

```python
from coactive.client import Coactive
from coactive import StorageTypeEnum

coactive_client = Coactive(
  client_id="YOUR_CLIENT_ID",
  client_secret="YOUR_CLIENT_SECRET",
  base_url="https://custom-domain.com/your/path"
)
```

## Mypy Annotations
The SDK methods and type definitions are all annotated with 
mypy so consumers can leverage autocomplete and intellisense. 
![autocomplete](./assets/autocomplete.png)

## Beta status

This SDK is in beta, and there may be breaking changes between 
versions without a major version update. Therefore, we recommend pinning 
the package version to a specific version in your pyproject.toml file. 
This way, you can install the same version each time without breaking 
changes unless you are intentionally looking for the latest version.

## Contributing

While we value open-source contributions to this SDK, this library is 
generated programmatically. Additions made directly to this library would 
have to be moved over to our generation code, otherwise they would be 
overwritten upon the next generated release. Feel free to open a PR as a 
proof of concept, but know that we will not be able to merge it as-is. 
We suggest opening an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
