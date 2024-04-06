import requests
from requests.exceptions import RequestException


def get_request(*args, **kwargs) -> str:
    """Synchronous GET request with requests."""
    try:
        response = requests.get(*args, **kwargs)
        response.raise_for_status()  # Löst eine Exception für HTTP Fehlercodes aus
        return response.text
    except RequestException as e:
        return str(e)  # Gibt die Fehlermeldung als String zurück


def get_request_as_json(*args, **kwargs) -> str:
    """Synchronous GET request with requests."""
    try:
        response = requests.get(*args, **kwargs)
        response.raise_for_status()  # Löst eine Exception für HTTP Fehlercodes aus
        return response.json()
    except RequestException as e:
        return str(e)  # Gibt die Fehlermeldung als String zurück
    