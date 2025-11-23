# api.py
import requests
import urllib.parse

BASE_URL = "https://addfriendmain-wotaxxdev.vercel.app/add?uid=4151162997&password=48dec99693e90fd932ef260785a5846e3812ae2893ef086496961fb2d1d46076&region=eu&adduid={uid}"

def call_addfriend_api(uid: str):
    """
    Call the add-friend API.
    Returns only a dict with either 'message' or 'error' if present, else {}.
    """
    try:
        url = BASE_URL.format(uid=urllib.parse.quote(str(uid)))
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Check top-level main_response first
        main_resp = data.get("main_response", {})
        result = {}
        if isinstance(main_resp, dict):
            if "message" in main_resp:
                result["message"] = main_resp["message"]
            elif "error" in main_resp:
                result["error"] = main_resp["error"]

        # fallback: top-level keys if main_response missing
        if not result:
            if "message" in data:
                result["message"] = data["message"]
            elif "error" in data:
                result["error"] = data["error"]

        return result

    except Exception:
        # Never leak API URLs, just return empty dict
        return {}
