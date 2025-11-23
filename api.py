# api.py
import requests
import urllib.parse

BASE_URL = "https://addfriendmain-wotaxxdev.vercel.app/add?uid=4151162997&password=48dec99693e90fd932ef260785a5846e3812ae2893ef086496961fb2d1d46076&region=eu&adduid={uid}"

def call_addfriend_api(uid: str):
    """
    Calls the API with the given adduid.
    Returns a dict containing only the JSON response, or {} on any error.
    """
    try:
        url = BASE_URL.format(uid=urllib.parse.quote(str(uid)))
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Only keep 'message' or 'error' keys
        filtered = {}
        if "message" in data:
            filtered["message"] = data["message"]
        if "error" in data:
            filtered["error"] = data["error"]
        return filtered
    except Exception:
        # On network error, timeout, HTTP 500, or invalid JSON, return empty dict
        return {}
