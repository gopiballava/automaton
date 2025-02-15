import requests
from requests.compat import urljoin


BACKEND_BASE_URL = 'http://216.137.189.35:9090/'


def send_dylos(name: str, small: int, large: int):
    requests.get(
        url=urljoin(BACKEND_BASE_URL, 'sensor/dylos'),
        params={
            "name": name,
            "small": small,
            "large": large,
        },
    )


def send_raw(name: str, count: int):
    requests.get(
        url=urljoin(BACKEND_BASE_URL, 'sensor/raw_particle'),
        params={
            "name": name,
            "raw": count,
        },
    )

def send_pms(name: str, small: int, medium: int, large: int):
    requests.get(
        url=urljoin(BACKEND_BASE_URL, 'sensor/plantower'),
        params={
            "name": name,
            "count0.5": small,
            "count2.5": medium,
            "count10": large,
        },
    )
