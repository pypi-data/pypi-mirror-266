from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _start_output_tracking(AUTH_TOKEN, URL, LIVE_CHANNEL_ID, DEBUG):

    API_URL = f"{URL}/api/liveChannel/{LIVE_CHANNEL_ID}/startOutputTracking"

    # Create header for the request
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()
    except:
        _api_exception_handler(RESPONSE, "Start Output Tracking Failed")