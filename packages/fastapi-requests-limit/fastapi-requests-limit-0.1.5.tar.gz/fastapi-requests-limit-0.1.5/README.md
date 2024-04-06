# FastAPI Rate Limit Controller


## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [Additional Features](#additional-features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
## Description

This FastAPI library enables developers to control and limit the number of requests made to API endpoints, providing an effective solution to prevent server overload and enhance security. By using Redis and local memory storage, the library keeps a record of requests per endpoint, tracking when the last request was made and the number of requests within a specific time interval. If an endpoint reaches its allowed request limit within the defined interval, the library will temporarily block further requests to that endpoint, helping to prevent API abuse. This beta version currently supports Redis and local memory as storage options, with plans to expand to more types of storage in the future.

## Installation

```bash
pip install fastapi-request-limit
```


## Usage

Explain how to use your library with simple examples. Include code blocks and descriptions for each example to guide the user. For instance:

```python

from fastapi_requests_limit.configuration import Limiter

limiter = Limiter(host="localhost", port="6379", storage_engine='redis')
```
This example requires installing Redis and having a set host. If you don't want to use Redis but rather local memory, The configuration would be as follows:

```python

from fastapi_requests_limit.configuration import Limiter

limiter = Limiter(storage_engine='memory')
```
Then you must limit the endpoint you want.
```python
from fastapi_requests_limit.limiter_rest import LimiterDecorator as limiter_decorator


@app.get("/")
@limiter_decorator(time=5, count_target=3)
async def read_users(request: Request):
    return [{"username": "Rick"}, {"username": "Morty"}]

```



## Configurations

### Local memory
```python
limiter = Limiter(storage_engine='memory')
```

### Redis server
```python
limiter = Limiter(host="<host>", port="<port>", storage_engine='redis')
```

### Decorator
```python
@limiter_decorator(time=5, count_target=3)

```
## Example

```python

from fastapi import FastAPI, Request
from fastapi_requests_limit.configuration import Limiter
from fastapi_requests_limit.limiter_rest import LimiterDecorator as limiter_decorator

app = FastAPI()
limiter = Limiter(host="localhost", port="6379", storage_engine='redis')


@app.get("/")
@limiter_decorator(time=5, count_target=3)
async def read_users(request: Request):
    return [{"username": "Rick"}, {"username": "Morty"}]


```
## Project Status

If you're interested in contributing to this project, we welcome your contributions! Please read our CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.txt) file for details.
