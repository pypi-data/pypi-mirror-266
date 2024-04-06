from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _get_live_channel_schedule_events(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/liveScheduleEvent"

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

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Get Live Channel Schedule Events failed")

