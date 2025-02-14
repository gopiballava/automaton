import unittest
from . import get_current_weather_at


class TestCurrentWeather(unittest.TestCase):
    def test_weather_berlin(self):
        current = get_current_weather_at(lat=52.5244, lon=13.4105)
        # Global warming may break this end-to-end test.
        self.assertLess(current.temp_f, 120)


if __name__ == '__main__':
    unittest.main()
