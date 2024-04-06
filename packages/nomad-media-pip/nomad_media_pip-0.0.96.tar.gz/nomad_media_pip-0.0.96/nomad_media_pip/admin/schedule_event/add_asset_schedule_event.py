from nomad_media_pip.admin.schedule_event.event_types import _EVENT_TYPES
from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _add_asset_schedule_event(AUTH_TOKEN, URL, CHANNEL_ID, ASSET, IS_LOOP,
                              DURATION_TIME_CODE, PREVIOUS_ID, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/liveScheduleEvent" 

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    # Build the payload BODY
    BODY = {
        "isLoop": IS_LOOP,
        "channelId": CHANNEL_ID,
        "durationTimeCode": DURATION_TIME_CODE,
        "previousId": PREVIOUS_ID,
        "type": {
            "id": _EVENT_TYPES["videoAsset"],
            "description": "Video-Asset"
        },
        "asset": ASSET,
    }

    if DEBUG:
        print(f"API URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
    
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Add Asset Schedule Event failed")

