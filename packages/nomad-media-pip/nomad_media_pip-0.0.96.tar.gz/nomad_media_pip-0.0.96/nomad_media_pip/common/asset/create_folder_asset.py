from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_folder_asset(AUTH_TOKEN, URL, PARENT_ID, DISPLAY_NAME, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{PARENT_ID}/create-folder"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "displayName": DISPLAY_NAME
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Create folder asset failed")