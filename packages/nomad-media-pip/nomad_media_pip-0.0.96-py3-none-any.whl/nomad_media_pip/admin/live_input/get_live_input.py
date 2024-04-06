from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _get_live_input(AUTH_TOKEN, URL, INPUT_ID, DEBUG):
    API_URL = f"{URL}/api/liveInput/{INPUT_ID}"

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

        # If not found return None
        if (not RESPONSE.ok):
            raise Exception()

        return RESPONSE.json()


    except:
        _api_exception_handler(RESPONSE, f"Get Live Input with ID {INPUT_ID} failed")

