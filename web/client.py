import requests
from requests.compat import urljoin


BACKEND_BASE_URL = 'http://216.137.189.35:9090/'


def send_dylos(name: str, small: int, large: int):
    requests.post(
        url=urljoin(BACKEND_BASE_URL, 'sensor/dylos'),
        json={
            "name": name,
            "small": small,
            "large": large,
        },
    )
