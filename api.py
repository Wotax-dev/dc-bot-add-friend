import requests

# ---------- ADD FRIEND API ----------
BASE_ADD_URL = (
    "https://addfriendmain-wotaxxdev.vercel.app/add"
    "?uid=4188062547"
    "&password=2363145937f1f2141aa6028d22d0d97b0a77ee32dbad52758c9b4f3c36f63b1a"
    "&region=br"
    "&adduid={uid}"
)

# ---------- REMOVE FRIEND API ----------
BASE_REMOVE_URL = (
    "https://addfriendmain-wotaxxdev.vercel.app/remove"
    "?uid=4188062547"
    "&password=2363145937f1f2141aa6028d22d0d97b0a77ee32dbad52758c9b4f3c36f63b1a"
    "&region=br"
    "&adduid={uid}"
)

def call_addfriend_api(uid: str):
    """
    Call the friend add API with a given UID.
    Returns a dictionary with either 'message' or 'error'.
    """
    url = BASE_ADD_URL.format(uid=uid)
    return _call_api(url)


def call_removefriend_api(uid: str):
    """
    Call the friend remove API with a given UID.
    Returns a dictionary with either 'message' or 'error'.
    """
    url = BASE_REMOVE_URL.format(uid=uid)
    return _call_api(url)


# ---------- Shared helper ----------
def _call_api(url: str):
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

    except requests.exceptions.HTTPError:
        return {"error": f"API returned an error ({resp.status_code}). Please try again later."}
    except requests.exceptions.RequestException:
        return {"error": "Network error. Could not reach the API."}
