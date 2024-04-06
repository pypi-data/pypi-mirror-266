from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _share_asset(AUTH_TOKEN, URL, ASSET_ID, NOMAD_USERS, EXTERNAL_USERS,
                 SHARE_DURATION_IN_HOURS, DEBUG):
    
    API_URL = f"{URL}/api/asset/{ASSET_ID}/share"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "assetId": ASSET_ID,
        "nomadUsers": NOMAD_USERS,
        "externalUsers": EXTERNAL_USERS,
        "durationInHours": SHARE_DURATION_IN_HOURS
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Share asset failed")