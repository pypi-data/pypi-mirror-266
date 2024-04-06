from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _update_asset_language(AUTH_TOKEN, URL, ASSET_ID, LANGUAGE_ID, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/language"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "languageId": LANGUAGE_ID
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Update asset language failed")