from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _deactivate_content_user_track(AUTH_TOKEN, URL, SESSION_ID, CONTENT_ID,
                                CONTENT_DEFINITION_ID, DEACTIVATE, DEBUG):

    API_URL = f"{URL}/api/content/{CONTENT_DEFINITION_ID}/user-track/{CONTENT_ID}/{SESSION_ID}/{DEACTIVATE}"

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
        _api_exception_handler(RESPONSE, "Deactivate content user track failed")