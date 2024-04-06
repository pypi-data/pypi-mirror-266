import pytest

from pathlib import Path
from m_car_api.objects import APIReturn, VehicleReturn


@pytest.fixture(scope="session")
def vehicle_json_path() -> Path:
    return Path(__file__).parent / "vehicle_return.json"


@pytest.fixture(scope="session")
def vehicle_json(vehicle_json_path: str) -> str:
    with open(vehicle_json_path) as f:
        return f.read()


def test_vehicle_check(vehicle_json: str):
    result = APIReturn[VehicleReturn].model_validate_json(vehicle_json)
    assert isinstance(result, APIReturn[VehicleReturn])
    first_vehicle = result.data.vehicles[0]
    first_vehicle.id == 10326
    first_vehicle.license_plate == "B-MS 4309"
