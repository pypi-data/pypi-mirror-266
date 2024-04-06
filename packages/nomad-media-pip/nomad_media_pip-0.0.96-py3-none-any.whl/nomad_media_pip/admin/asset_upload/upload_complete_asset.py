from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _upload_complete_asset(AUTH_TOKEN, URL, ID, DEBUG):

    API_URL = f"{URL}/api/asset/upload/{ID}/complete"
        
    # Create header for the request
    HEADERS = {
      	"Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Upload complete asset failed")

