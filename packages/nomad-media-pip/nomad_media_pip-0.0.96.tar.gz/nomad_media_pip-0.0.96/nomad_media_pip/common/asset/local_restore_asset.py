from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _local_restore_asset(AUTH_TOKEN, URL, ASSET_ID, PROFILE, DEBUG):

    API_URL = f"{URL}/api/asset/{ASSET_ID}/localRestore"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "profile": PROFILE
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Local restore asset failed")