from typing import Union, Optional
from dataclasses import dataclass
from pyowm import OWM

owm = OWM('32b634f0223c19bc4583e397bbbe2e38')
mgr = owm.weather_manager()


@dataclass
class CurrentWeather:
    temp_c: int
    temp_f: int
    uv_index: Optional[str]
    cloud_cover: str


def get_current_weather_at(lat: float, lon: float) -> CurrentWeather:
    one_call = mgr.one_call(lat=lat, lon=lon)
    retv = CurrentWeather(
        temp_f=one_call.current.temperature("fahrenheit")["temp"],
        temp_c=one_call.current.temperature("celsius")["temp"],
        uv_index=None,
        cloud_cover=one_call.current.clouds)
    if one_call.current.uvi:
        retv.uv_index = one_call.current.uvi
    return retv
