from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_schedule_item_live_channel(AUTH_TOKNE, URL, SCHEUDLE_ID, DAYS, DURATION_TIME_CODE,
                                       END_TIME_CODE, LIVE_CHANNEL, PREVIOUS_ITEM, TIME_CODE, 
                                       DEBUG):
    
    API_URL = f"{URL}/api/admin/schedule/{SCHEUDLE_ID}/item"
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKNE,
        "Content-Type": "application/json"
    }

    BODY = {
        "days": DAYS,
        "durationTimeCode": DURATION_TIME_CODE,
        "endTimeCode": END_TIME_CODE,
        "liveChannel": LIVE_CHANNEL,
        "previousItem": PREVIOUS_ITEM,
        "scheduleItemType": "1",
        "sourceType": "4",
        "timeCode": TIME_CODE
    }
    
    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Schedule Item Live Channel Failed")