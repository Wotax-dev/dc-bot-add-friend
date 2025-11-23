# api.py
import requests
import urllib.parse

BASE_URL = "https://addfriendmain-wotaxxdev.vercel.app/add?uid=4151162997&password=48dec99693e90fd932ef260785a5846e3812ae2893ef086496961fb2d1d46076&region={region}&adduid={uid}"

def call_addfriend_api(uid: str, region: str = "eu"):
    url = BASE_URL.format(uid=urllib.parse.quote(str(uid)), region=urllib.parse.quote(region.lower()))
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        main_resp = data.get("main_response", {})
        if "message" in main_resp:
            return {"message": main_resp["message"]}
        elif "error" in main_resp:
            return {"error": main_resp["error"]}
        else:
            return {"error": "Unexpected API response."}
    except requests.exceptions.HTTPError as e:
        # Only show status code and reason, hide URL
        return {"error": f"Network error: {e.response.status_code} {e.response.reason}"}
    except requests.exceptions.RequestException:
        # Generic network error
        return {"error": "Network error: Unable to reach the API."}
