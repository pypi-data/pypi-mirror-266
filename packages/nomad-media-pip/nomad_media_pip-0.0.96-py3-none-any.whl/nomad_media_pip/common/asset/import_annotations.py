from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _import_annotations(AUTH_TOKEN, URL, ASSET_ID, ANNOTATIONS, DEBUG):

    API_URL = f"{URL}/api/asset/{ASSET_ID}/annotation/import"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(ANNOTATIONS, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(ANNOTATIONS))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Import annotations failed")