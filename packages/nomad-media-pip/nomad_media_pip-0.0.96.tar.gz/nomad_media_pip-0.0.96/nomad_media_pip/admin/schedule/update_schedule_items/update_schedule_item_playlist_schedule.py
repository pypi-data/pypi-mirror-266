from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.schedule.get_schedule_item import _get_schedule_item

import requests, json

def _update_schedule_item_playlist_schedule(AUTH_TOKEN, URL, ID, ITEM_ID, DAYS,
                                            DURATION_TIME_CODE, END_TIME_CODE, 
                                            PLAYLIST_SCHEDULE, TIME_CODE, DEBUG):
    
        SCHEDULE_ITEM = _get_schedule_item(AUTH_TOKEN, URL, ID, ITEM_ID, DEBUG)
    
        API_URL = f"{URL}/api/admin/schedule/{ID}/item/{ITEM_ID}"
    
        HEADERS = {
            "Authorization": "Bearer " + AUTH_TOKEN,
            "Content-Type": "application/json"
        }
    
        BODY = {
            "days": DAYS or SCHEDULE_ITEM.get("days"),
            "durationTimeCode": DURATION_TIME_CODE or SCHEDULE_ITEM.get("durationTimeCode"),
            "endTimeCode": END_TIME_CODE or SCHEDULE_ITEM.get("endTimeCode"),
            "playlistSchedule": PLAYLIST_SCHEDULE or SCHEDULE_ITEM.get("playlistSchedule"),
            "scheduleItemType": "2",
            "sourceType": "1",
            "timeCode": TIME_CODE or SCHEDULE_ITEM.get("timeCode")
        }
    
        if DEBUG:
            print(f"URL: {API_URL},\nMETHOD: PUT,\nBODY: {json.dumps(BODY, indent=4)}")
    
        try:
            RESPONSE = requests.put(API_URL, headers= HEADERS, data= json.dumps(BODY))
    
            if not RESPONSE.ok:
                raise Exception()
            
            return RESPONSE.json()
        except:
            _api_exception_handler(RESPONSE, "Update Schedule Item Playlist Schedule Failed")