from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _delete_tag_or_collection(AUTH_TOKEN, URL, TYPE, TAG_ID, DEBUG):

    API_URL = f"{URL}/api/admin/{TYPE}/{TAG_ID}"
        
    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: DELETE")

    try:
        # Send the request
        RESPONSE = requests.delete(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "delete tag or colleciton failed")

