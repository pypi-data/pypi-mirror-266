from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _update_asset(AUTH_TOKEN, URL, ASSET_ID, DISPLAY_NAME, DISPLAY_DATE, AVAILABLE_START_DATE,
                  AVAILABLE_END_DATE, CUSTOM_PROPERTIES, DEBUG):
    
    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "displayName": DISPLAY_NAME,
        "displayDate": DISPLAY_DATE,
        "availableStartDate": AVAILABLE_START_DATE,
        "availableEndDate": AVAILABLE_END_DATE,
        "customProperties": CUSTOM_PROPERTIES
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: PATCH\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.patch(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, "Update asset failed")