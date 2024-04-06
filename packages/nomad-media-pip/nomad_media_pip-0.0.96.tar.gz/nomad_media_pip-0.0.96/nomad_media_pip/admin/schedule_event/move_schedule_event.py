from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _move_schedule_event(AUTH_TOKEN, URL, CHANNEL_ID, SCHEDULE_EVENT_ID,
                         PREVIOUS_SCHEDULE_EVENT_ID, DEBUG):
    
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/liveScheduleEvent/{SCHEDULE_EVENT_ID}/move"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "previousScheduleEventId": PREVIOUS_SCHEDULE_EVENT_ID
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: PUT,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.put(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Move Schedule Event Failed")