import mujson
from datetime import datetime
from typing import Any, Generic, Literal, NamedTuple, TypeVar
from pydantic import BaseModel, Field, computed_field


class DeviceInfo(NamedTuple):
    owner_name: str = "unknown"
    device_info1: str = "Linux"
    device_info2: str = "amd64"
    os_info1: str = "Linux"
    os_info2: str = "6.8.2-generic"
    app_version: str = "4.31+(210440)"
    lang: str = "en"
    translation_dictionary_timestamp: datetime = datetime(year=2001, month=1, day=1)
    city_areas_timestamp: datetime = datetime(2020, 1, 3)

    def to_params(self) -> dict[str, Any]:
        return {
            "ownerName": self.owner_name,
            "deviceInfo1": self.device_info1,
            "deviceInfo2": self.device_info2,
            "osInfo1": self.os_info1,
            "osInfo2": self.os_info2,
            "appVersion": self.app_version,
            "lang": self.lang,
            "translationDictionaryTimestamp": self.translation_dictionary_timestamp.isoformat(
                sep=" "
            ),
            "cityAreasTimestamp": self.city_areas_timestamp.isoformat(sep=" "),
        }


class VehicleQuery(NamedTuple):
    user_latitude: float | None = None
    user_longitude: float | None = None
    fuel_level_filter_min: int = 0
    fuel_level_filter_max: int = 100
    vehicle_size_filter: tuple[str, ...] | None = None
    vehicle_engine_filter: str | None = None
    vehicle_seats_filter: tuple[int, ...] | None = None
    zoom_level: int = 10
    show_only_discounted_vehicles: bool = False
    show_fueling_stations: bool = False
    show_charging_stations: bool = False
    show_miles_partners: bool = False

    def to_params(
        self,
        latitude: float,
        longitude: float,
        latitude_delta: float,
        longitude_delta: float,
    ) -> dict[str, Any]:
        return {
            "latitude": latitude,
            "longitude": longitude,
            "latitudeDelta": latitude_delta,
            "longitudeDelta": longitude_delta,
            "userLatitude": self.user_latitude or latitude,
            "userLongitude": self.user_longitude or longitude,
            "FuelLevelFilterMin": self.fuel_level_filter_min,
            "FuelLevelFilterMax": self.fuel_level_filter_max,
            "VehicleSizeFilter": (
                ",".join(self.vehicle_size_filter) if self.vehicle_size_filter else None
            ),
            "vehicleEngineFilter": self.vehicle_engine_filter,
            "VehicleSeatsFilter": (
                ",".join(map(str, self.vehicle_seats_filter))
                if self.vehicle_seats_filter
                else None
            ),
            "zoomLevel": self.zoom_level,
            "showOnlyDiscountedVehicles": int(self.show_only_discounted_vehicles),
            "showFuelingStations": int(self.show_fueling_stations),
            "showChargingStations": int(self.show_charging_stations),
            "showMilesPartners": int(self.show_miles_partners),
        }


class RentalPrice(BaseModel):
    price: str
    unit: str
    discounted: bool = False
    description: str = ""
    discount_source: str | None = None


class ParkingPrice(BaseModel):
    price: str
    unit: str
    discounted: bool = False


class UnlockFee(BaseModel):
    price: str
    unit: str
    discounted: bool


class Destination(BaseModel):
    destination: str = Field(alias="Destination")


class DestinationWithPrice(Destination):
    city_id: str = Field(alias="idCity")
    price: str = Field(alias="Price")
    price_discounted: str | None = Field(alias="Price_discounted")


class CityToCityOptions(BaseModel):
    origin_city: str = Field(alias="OriginCity")
    destinations_raw: list[DestinationWithPrice] | None = Field(
        alias="Destinations", exclude=True
    )

    @property
    @computed_field
    def destinations(self) -> list[DestinationWithPrice]:
        return self.destinations_raw or []

    not_possible_destinations_raw: list[Destination] | None = Field(
        alias="NotPossibleDestinations", exclude=True
    )

    @property
    @computed_field
    def not_possible_destinations(self) -> list[Destination]:
        return self.not_possible_destinations_raw or []


class Vehicle(BaseModel):
    id: int = Field(alias="idVehicle")
    city_id: str = Field(alias="idCity")
    license_plate: str = Field(alias="LicensePlate")
    type: str = Field(alias="VehicleType")
    color: str = Field(alias="VehicleColor")
    size: Literal["S", "M", "L", "X", "P"] = Field(alias="VehicleSize")
    electric: bool = Field(alias="isElectric")
    latitude: float = Field(alias="Latitude")
    longitude: float = Field(alias="Longitude")
    distance_from_user_position: float = Field(alias="DistanceFromUserPosition")
    distance_from_middle_position: float = Field(alias="DistanceFromMiddlePosition")
    status: str = Field(alias="idVehicleStatus")
    gsm_coverage: int = Field(alias="GSMCoverage")
    satellite_number: int = Field(alias="SatelliteNumber")

    rental_price_row_1: str = Field(alias="RentalPrice_row1", exclude=True)
    rental_price_row_1_unit: str = Field(alias="RentalPrice_row1unit", exclude=True)
    rental_price_discounted: str | None = Field(
        alias="RentalPrice_discounted", exclude=True
    )
    rental_price_row_2: str = Field(alias="RentalPrice_row2", exclude=True)
    rental_price_discount_source: str | None = Field(
        alias="RentalPrice_discountSource", exclude=True
    )

    @computed_field
    @property
    def rental_price(self) -> RentalPrice:
        return RentalPrice(
            price=self.rental_price_row_1,
            unit=self.rental_price_row_1_unit,
            discounted=bool(self.rental_price_discounted),
            description=self.rental_price_row_2,
            discount_source=self.rental_price_discount_source,
        )

    parking_price_item: str = Field(alias="ParkingPrice", exclude=True)
    parking_price_discounted: bool | str | None = Field(
        alias="ParkingPrice_discounted", exclude=True
    )
    parking_price_unit: str = Field(alias="ParkingPrice_unit", exclude=True)

    @computed_field
    @property
    def parking_price(self) -> ParkingPrice:
        return ParkingPrice(
            price=self.parking_price_item,
            unit=self.parking_price_unit,
            discounted=bool(self.parking_price_discounted),
        )

    unlock_fee_item: str = Field(alias="UnlockFee", exclude=True)
    unlock_fee_discounted: str | None = Field(
        alias="UnlockFee_discounted", exclude=True
    )
    unlock_fee_unit: str = Field(alias="UnlockFee_unit", exclude=True)

    @computed_field
    @property
    def unlock_fee(self) -> UnlockFee:
        return UnlockFee(
            price=self.unlock_fee_item,
            unit=self.unlock_fee_unit,
            discounted=bool(self.unlock_fee_discounted),
        )

    fuel_percent: str = Field(alias="FuelPct")
    fuel_level_icon: int = Field(alias="FuelLevelIcon")
    remaining_range: str = Field(alias="RemainingRange")
    ev_plugged: bool = Field(alias="EVPlugged")
    fvd_price: str = Field(alias="FVDPrice")
    url_vehicle_image: str = Field(alias="URLVehicleImage")
    rookie_delay_txt: str = Field(alias="RookieDelayTxt")
    number_days_rookies_delay: int = Field(alias="nDaysRookieDelay")
    premium_restricted_txt: str = Field(alias="PremiumRestrictedTxt")
    city_to_city_options_string: str | None = Field(
        alias="CityToCityOptions", exclude=True
    )

    @computed_field
    @property
    def city_to_city_options(self) -> CityToCityOptions:
        return CityToCityOptions.model_validate_json(self.city_to_city_options_string)

    json_vehicle_damages_input: str | None = Field(
        alias="JSONVehicleDamages", exclude=True
    )

    @computed_field
    @property
    def json_vehicle_damages(self) -> list[dict[str, Any]]:
        if self.json_vehicle_damages_input is None:
            return []
        else:
            return mujson.loads(self.json_vehicle_damages_input)

    json_vehicle_banner: str | None = Field(alias="JSONVehicleBanner")


class VehicleResponse(BaseModel):
    result: str = Field(alias="Result")
    response_text: str | None = Field(alias="ResponseText")
    id_vehicle_booked: str | None = Field(alias="idVehicleBooked")
    id_ride: str | None = Field(alias="idRide")
    id_vehicle_in_ride: str | None = Field(alias="idVehicleInRide")
    nearest_id_city: str | None = Field(alias="NearestIdCity")
    live_payment: bool = Field(alias="LivePayment")
    top_up_required: bool = Field(alias="TopUpRequired")
    user_app_version: str | float = Field(alias="userAppVersion")
    n_filter_elements: int = Field(alias="nFilterElements")
    user_in_ops_mode: bool = Field(alias="UserInOpsMode")
    special_airport_rate: str | None = Field(alias="SpecialAirportRate")
    special_airport_rate_e: str | None = Field(alias="SpecialAirportRate_E")
    special_airport_rate_2: str | None = Field(alias="SpecialAirportRate_2")
    special_airport_rate_e_2: str | None = Field(alias="SpecialAirportRate_E_2")
    uses_ppc: bool = Field(alias="UsesPPC")
    current_subscription: str | None = Field(alias="CurrentSubscription")
    json_city_areas: str = Field(alias="JSONCityAreas")
    city_areas_timestamp: datetime = Field(alias="CityAreasTimestamp")
    additional_info: str = Field(alias="AdditionalInfo")


class VehicleReturn(BaseModel):
    response: VehicleResponse = Field(alias="response")
    vehicles: list[Vehicle] = Field(alias="vehicles")


APIData = TypeVar("APIData")


class APIReturn(BaseModel, Generic[APIData]):
    result: str = Field(alias="Result")
    response_text: str | None = Field(alias="ResponseText")
    data: APIData = Field(alias="Data")
