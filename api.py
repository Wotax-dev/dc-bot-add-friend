# api.py
import requests
import urllib.parse

BASE_URL = (
    "https://addfriendmain-wotaxxdev.vercel.app/add?"
    "uid=4151162997&password=48dec99693e90fd932ef260785a5846e3812ae2893ef086496961fb2d1d46076"
    "&region=eu&adduid={uid}"
)

def call_addfriend_api(uid: str):
    """
    Call the add-friend API.
    Returns dict with either 'message' or 'error' if found, else {}.
    """
    try:
        url = BASE_URL.format(uid=urllib.parse.quote(str(uid)))
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception:
        # Never leak API URLs or errors
        return {}
