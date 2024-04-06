from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _get_live_inputs(AUTH_TOKEN, URL, DEBUG):
    API_URL = f"{URL}/api/liveInput"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: GET")

    try:
        # Send the request
        RESPONSE = requests.get(API_URL, headers= HEADERS)
    
        if (not RESPONSE.ok):
            raise Exception()

        # Return JSON response
        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Get Live Inputs failed")

