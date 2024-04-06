from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _remove_asset_schedule_event(AUTH_TOKEN, URL, CHANNEL_ID, SCHEDULE_EVENT_ID, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/liveScheduleEvent/{SCHEDULE_EVENT_ID}"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"API URL: {API_URL}\nMETHOD: DELETE")

    try:
        # Send the request
        RESPONSE = requests.delete(API_URL, headers= HEADERS)
    
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Remove Asset Schedule Event failed")