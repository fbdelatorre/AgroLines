import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def check_health(base_url: str, timeout: float = 3.0) -> bool:
    try:
        with urlopen(f"{base_url.rstrip('/')}/health", timeout=timeout) as response:
            data = json.load(response)
            return (
                response.status == 200
                and isinstance(data, dict)
                and data.get("status") == "ok"
                and data.get("service") == "agrolines"
            )
    except (HTTPError, URLError, OSError, ValueError):
        return False
