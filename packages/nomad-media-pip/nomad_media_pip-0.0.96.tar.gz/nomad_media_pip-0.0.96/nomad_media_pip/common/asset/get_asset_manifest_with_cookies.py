from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_asset_manifest_with_cookies(AUTH_TOKEN, URL, ASSET_ID, COOKIE_ID, API_TYPE, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/set-cookies/{COOKIE_ID}" if API_TYPE == "admin" else f"{URL}/api/asset/{ASSET_ID}/set-cookies/{COOKIE_ID}"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Get asset manifest with cookies failed")