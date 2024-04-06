from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _get_search(AUTH_TOKEN, URL, ID, API_TYPE, DEBUG):
    API_URL = f"{URL}/api/{API_TYPE}/search/{ID}"

    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    try:
        # Send the request
        RESPONSE = requests.get(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Searching failed")