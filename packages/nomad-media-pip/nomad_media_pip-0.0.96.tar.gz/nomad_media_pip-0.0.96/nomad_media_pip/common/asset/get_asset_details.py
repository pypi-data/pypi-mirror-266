from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_asset_details(AUTH_TOKEN, URL, ASSET_ID, API_TYPE, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/detail" if API_TYPE == "admin" else f"{URL}/api/asset/{ASSET_ID}/detail"

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
        _api_exception_handler(RESPONSE, "Get asset details failed")