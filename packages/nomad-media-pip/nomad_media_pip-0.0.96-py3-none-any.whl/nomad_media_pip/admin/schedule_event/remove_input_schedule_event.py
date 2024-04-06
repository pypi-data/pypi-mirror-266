from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _remove_input_schedule_event(AUTH_TOKEN, URL, CHANNEL_ID, INPUT_ID, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/liveScheduleEvent/{INPUT_ID}" 

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"API URL: {API_URL}\nMETHOD: DELETE")

    try:
        RESPONSE = requests.delete(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
    except:
        _api_exception_handler(RESPONSE, "Remove Input Schedule Event failed")