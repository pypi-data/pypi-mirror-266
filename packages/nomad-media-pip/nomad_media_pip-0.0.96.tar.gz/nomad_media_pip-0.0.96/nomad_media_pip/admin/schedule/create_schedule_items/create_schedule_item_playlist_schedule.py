from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_schedule_item_playlist_schedule(AUTH_TOKN, URL, SCHEUDLE_ID, DAYS, 
                                            DURATION_TIME_CODE, END_TIME_CODE, 
                                            PLAYLIST_SCHEDULE, PREVIOUS_ITEM, TIME_CODE, 
                                            DEBUG):
        
        API_URL = f"{URL}/api/admin/schedule/{SCHEUDLE_ID}/item"
        
        HEADERS = {
            "Authorization": "Bearer " + AUTH_TOKN,
            "Content-Type": "application/json"
        }
        
        BODY = {
            "days": DAYS,
            "durationTimeCode": DURATION_TIME_CODE,
            "endTimeCode": END_TIME_CODE,
            "playlistSchedule": PLAYLIST_SCHEDULE,
            "previousItem": PREVIOUS_ITEM,
            "scheduleItemType": "2",
            "sourceType": "1",
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
            _api_exception_handler(RESPONSE, "Create Schedule Item Playlist Schedule Failed")