from uuid import UUID, uuid4
import pytest
from m_car_api import vehicles, vehicles_meters_around_location


@pytest.fixture
def device_key(request: pytest.FixtureRequest) -> str:
    device_key = request.config.cache.get("mapi/device-key", None)
    if device_key is None:
        device_key = str(uuid4())
        request.config.cache.set("mapi/device-key", device_key)
    return device_key


def test_vehicles(device_key: str) -> None:
    response = vehicles(
        device_key=device_key,
        lat=52.520008,
        lon=13.404954,
        latitude_delta=0.1,
        longitude_delta=0.1,
    )
    assert isinstance(response, list)


def test_vehicles_meters_around_location(device_key: str) -> None:
    response = vehicles_meters_around_location(
        device_key=device_key,
        lat=52.520008,
        lon=13.404954,
        meters=500,
    )
    assert isinstance(response, list)
