from __future__ import annotations
from typing import Any
import requests
from base64 import b64decode
from urllib.parse import urljoin
from pyproj import Geod

from m_car_api.const import U_HEL_URL_PATH, V_URL_PATH, DEFAULT_ROOT_URL
from m_car_api.objects import (
    DeviceInfo,
    Vehicle,
    VehicleQuery,
    VehicleReturn,
    APIReturn,
)

geod = Geod(ellps="WGS84")


class SubAPI:
    def __init__(self, mapi: MApi) -> None:
        self.mapi = mapi

    @property
    def device_key(self) -> str:
        return self.mapi.device_key

    @property
    def root_url(self) -> str:
        return self.mapi.root_url

    def _hello_if_not_done(self) -> bool:
        return self.mapi.hello_if_not_done()


class VehiclesSearchAPI(SubAPI):
    def __init__(
        self,
        mapi: MApi,
        lat: float,
        lon: float,
        latitude_delta: float,
        longitude_delta: float,
        query: VehicleQuery | None = None,
    ) -> None:
        super().__init__(mapi)
        self.lat = lat
        self.lon = lon
        self.latitude_delta = latitude_delta
        self.longitude_delta = longitude_delta
        self.query = query or VehicleQuery()

    def raw_json_response(self, path: str = V_URL_PATH) -> str:
        self._hello_if_not_done()
        vehicles_url = urljoin(self.root_url, path)
        params = self.query.to_params(
            latitude=self.lat,
            longitude=self.lon,
            latitude_delta=self.latitude_delta,
            longitude_delta=self.longitude_delta,
        )
        params["deviceKey"] = self.device_key
        response = requests.get(vehicles_url, params=params)
        response.raise_for_status()
        return response.text

    def vehicles_return(self) -> VehicleReturn:
        result = APIReturn[VehicleReturn].model_validate_json(self.raw_json_response())
        if result.result != "OK":
            raise ValueError(result.message)
        return result.data


class MApi:
    def __init__(self, device_key: str, root_url: str = DEFAULT_ROOT_URL) -> None:
        self.device_key = device_key
        self.root_url = root_url
        self._hello_done = False

    def hello(
        self, device_info: DeviceInfo | None = None, path: str = U_HEL_URL_PATH
    ) -> bool:
        device_info = device_info or DeviceInfo()
        url = urljoin(self.root_url, path)
        params = {
            "deviceKey": self.device_key,
            **device_info.to_params(),
        }
        response = requests.get(url, params=params)
        response.raise_for_status()

        result = response.json()["Result"] == "ok"
        if result:
            self._hello_done = True
        return result

    def hello_if_not_done(self, device_info: DeviceInfo | None = None) -> bool:
        if not self._hello_done:
            return self.hello(device_info=device_info)
        return True

    def vehicles_return(
        self,
        lat: float,
        lon: float,
        latitude_delta: float,
        longitude_delta: float,
        query: VehicleQuery | None = None,
    ) -> VehicleReturn:
        return VehiclesSearchAPI(
            mapi=self,
            lat=lat,
            lon=lon,
            latitude_delta=latitude_delta,
            longitude_delta=longitude_delta,
            query=query,
        ).vehicles_return()

    def vehicles(
        self,
        lat: float,
        lon: float,
        latitude_delta: float,
        longitude_delta: float,
        query: VehicleQuery | None = None,
    ) -> dict[str, Any]:
        return self.vehicles_return(
            lat=lat,
            lon=lon,
            latitude_delta=latitude_delta,
            longitude_delta=longitude_delta,
            query=query,
        ).vehicles

    def vehicles_return_meters_around_location(
        self, lat: float, lon: float, meters: float, query: VehicleQuery | None = None
    ) -> VehicleReturn:
        lon_top_left, lat_top_left, _ = geod.fwd(lon, lat, 315, meters)
        lon_bottom_right, lat_bottom_right, _ = geod.fwd(lon, lat, 135, meters)
        lat_delta = abs(lat_top_left - lat_bottom_right)
        lon_delta = abs(lon_top_left - lon_bottom_right)
        return self.vehicles_return(
            lat=lat,
            lon=lon,
            latitude_delta=lat_delta,
            longitude_delta=lon_delta,
            query=query,
        )

    def vehicles_meters_around_location(
        self, lat: float, lon: float, meters: float, query: VehicleQuery | None = None
    ) -> dict[str, Any]:
        return self.vehicles_return_meters_around_location(
            lat=lat,
            lon=lon,
            meters=meters,
            query=query,
        ).vehicles


def vehicles(
    device_key: str,
    lat: float,
    lon: float,
    latitude_delta: float,
    longitude_delta: float,
    query: VehicleQuery | None = None,
) -> list[Vehicle]:
    return MApi(device_key=device_key).vehicles(
        lat=lat,
        lon=lon,
        latitude_delta=latitude_delta,
        longitude_delta=longitude_delta,
        query=query,
    )


def vehicles_meters_around_location(
    device_key: str,
    lat: float,
    lon: float,
    meters: float,
    query: VehicleQuery | None = None,
) -> list[Vehicle]:
    return MApi(device_key=device_key).vehicles_meters_around_location(
        lat=lat,
        lon=lon,
        meters=meters,
        query=query,
    )
