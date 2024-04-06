from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_asset_ad_break(AUTH_TOKEN, URL, ASSET_ID, TIME_CODE, TAGS, LABELS, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/adbreak"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "id": ASSET_ID,
        "timecode": TIME_CODE
    }

    if TAGS:
        BODY["tags"] = TAGS

    if LABELS:
        BODY["labels"] = LABELS

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Create ad break failed")