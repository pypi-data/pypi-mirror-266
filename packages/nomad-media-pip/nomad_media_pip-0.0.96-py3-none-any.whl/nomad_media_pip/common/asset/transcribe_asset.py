from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests , json

def _transcribe_asset(AUTH_TOKEN, URL, ASSET_ID, TRANSCRIPT_ID, TRANSCRIPT, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/transcribe/{TRANSCRIPT_ID}"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(TRANSCRIPT, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(TRANSCRIPT))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Transcribe asset failed")

