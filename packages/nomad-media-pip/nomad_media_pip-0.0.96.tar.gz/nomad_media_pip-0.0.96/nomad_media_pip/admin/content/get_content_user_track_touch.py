from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_content_user_track_touch(AUTH_TOKEN, URL, CONTNET_ID, CONTENT_DEFINITION_ID, 
                                  DEBUG):
    API_URL = f"{URL}/api/content/{CONTENT_DEFINITION_ID}/user-track/{CONTNET_ID}/touch"

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
        _api_exception_handler(RESPONSE, "Get content user track touch failed")