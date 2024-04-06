import time

import pytest
from fastapi import FastAPI, Request
from httpx import AsyncClient

from fastapi_requests_limit.configuration import Limiter
from fastapi_requests_limit.limiter_rest import LimiterDecorator as limiter_decorator
from fastapi_requests_limit.storages.memory import MemoryStorage

from .test_constans import COUNT_LIMIT, TIME_LIMIT


@pytest.fixture()
def config_limiter():
    Limiter(storage_engine="memory")


@pytest.fixture
def test_app(config_limiter):
    app = FastAPI()

    @app.get("/test")
    @limiter_decorator(time=TIME_LIMIT, count_target=COUNT_LIMIT)
    async def root(request: Request):
        return {"message": "Tomato"}

    yield app
    MemoryStorage.clear()


@pytest.fixture
async def test_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.mark.parametrize(
    "additional_request, sleep_time, expected_status_code",
    [(False, 0, 200), (True, 0, 405), (True, TIME_LIMIT, 200)],
)
@pytest.mark.anyio
async def test_limiter_behavior(
    test_client, additional_request, sleep_time, expected_status_code
):
    test_client
    for _ in range(COUNT_LIMIT):
        response = await test_client.get("/test")
        assert response.status_code == 200

    if sleep_time > 0:
        time.sleep(sleep_time)

    if additional_request:
        response = await test_client.get("/test")
        assert response.status_code == expected_status_code
