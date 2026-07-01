import json

import uasyncio as asyncio
import _thread

import urequests

import lvgl as lv

from core.hw import connect_wifi
from core.ui import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, VIEWPORT_OFFX, VIEWPORT_OFFY
from core.app import BasicApp


_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain shower",
    81: "Moderate rain shower",
    82: "Violent rain shower",
    85: "Slight snow shower",
    86: "Heavy snow shower",
    95: "Thunderstorm",
    96: "Slight hail thunderstorm",
    99: "Heavy hail thunderstorm",
}

# https://api.open-meteo.com/v1/forecast?latitude=52.52,50.12,53.55&longitude=13.41,8.68,9.99&daily=temperature_2m_max,temperature_2m_min,weather_code&forecast_days=3
_CONFIG_PATH = "/config/weather_app/config.json"
_BASE_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherApp(BasicApp):
    def _read_config(self) -> dict | None:
        try:
            with open(_CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                return cfg
        except Exception:
            pass
        return None

    async def _get_weather(self) -> None:
        if not self.config:
            return
        if not await connect_wifi():
            print("Failed to connect to Wi-Fi")
            # todo: show message
            return

        latitude = ",".join(map(lambda x: str(x["latitude"]), self.config["cities"]))
        longitude = ",".join(map(lambda x: str(x["longitude"]), self.config["cities"]))
        forecast_days = self.config["forecast_days"]
        query_string = f"latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,weather_code&forecast_days={forecast_days}"
        full_url = f"{_BASE_URL}?{query_string}"

        flag = asyncio.ThreadSafeFlag()
        response = None

        def _get() -> None:
            nonlocal full_url
            nonlocal flag
            nonlocal response

            try:
                response = urequests.get(full_url)
                flag.set()
                return
            except Exception:
                pass
            flag.set()

        _thread.start_new_thread(_get, ())
        await flag.wait()  # ty:ignore[invalid-await]

        try:
            if response is not None and response.status_code == 200:
                data_array = response.json()
                for c in range(len(data_array)):
                    city = data_array[c]
                    daily = city["daily"]
                    for d in range(len(daily["time"])):
                        min = daily["temperature_2m_min"][d]
                        min_s = str(min) if min <= 0.0 else f"+{min}"
                        max = daily["temperature_2m_max"][d]
                        max_s = str(max) if max <= 0.0 else f"+{max}"
                        wc = daily["weather_code"][d]
                        wc_s = str(wc)
                        if wc in _WEATHER_CODES:
                            wc_s = _WEATHER_CODES[wc]
                        day = f"{daily['time'][d]}: {min_s}..{max_s} {wc_s}"
                        self.city_day_labels[c][d].set_text(day)
            else:
                print(
                    "Error Status Code:",
                    response.status_code if response is not None else 0,
                )
                # todo: show message
        except Exception as ex:
            print("Failed to parse response:", ex)
            # todo: show message

        if response is not None:
            response.close()

    def __init__(self):
        self.config = self._read_config()
        if not self.config:
            self.screen = lv.obj(None)  # ty:ignore[invalid-argument-type]
            self.label = lv.label(self.screen)
            self.label.set_long_mode(lv.label.LONG_MODE.WRAP)
            self.label.set_text(f'Failed to read config "{_CONFIG_PATH}"!')
            self.label.center()
            return

        self.screen = lv.obj(None)  # ty:ignore[invalid-argument-type]

        tv = lv.tileview(self.screen)
        tv.set_size(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        tv.set_pos(VIEWPORT_OFFX, VIEWPORT_OFFY)

        self.city_day_labels = []
        for c in range(len(self.config["cities"])):
            city = self.config["cities"][c]
            tile = tv.add_tile(c, 0, lv.DIR.LEFT | lv.DIR.RIGHT)
            stack = lv.obj(tile)
            stack.set_size(lv.pct(100), lv.pct(100))
            stack.set_layout(lv.LAYOUT.FLEX)
            stack.set_flex_flow(lv.FLEX_FLOW.COLUMN)
            stack.set_flex_align(
                lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.START
            )
            stack.set_style_pad_column(10, 0)
            stack.set_style_pad_all(5, 0)

            city_label = lv.label(stack)
            city_label.set_text(city["name"])
            self.city_day_labels.append([])
            for day in range(self.config["forecast_days"]):
                day_label = lv.label(stack)
                day_label.set_long_mode(lv.label.LONG_MODE.WRAP)
                day_label.set_width(lv.pct(90))
                day_label.set_text("-")
                self.city_day_labels[c].append(day_label)

    def __del__(self):
        if self.screen:
            self.screen.delete()

    def show(self):
        if self.screen:
            lv.screen_load(self.screen)
            asyncio.create_task(self._get_weather())

    def standby(self):
        pass

    def resume(self):
        pass
