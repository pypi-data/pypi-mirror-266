from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _move_schedule_item(AUTH_TOKEN, URL, ID, ITEM_ID, PREVIOUS_ITEM, DEBUG):
    
        API_URL = f"{URL}/api/admin/schedule/{ID}/item/{ITEM_ID}/move"
    
        HEADERS = {
            "Authorization": "Bearer " + AUTH_TOKEN,
            "Content-Type": "application/json"
        }
    
        BODY = {
            "previous_item": PREVIOUS_ITEM
        }
    
        if DEBUG:
            print(f"URL: {API_URL},\nMETHOD: POST")
    
        try:
            RESPONSE = requests.post(API_URL, headers= HEADERS, data=json.dumps(BODY))
    
            if not RESPONSE.ok:
                raise Exception()
            
            return RESPONSE.json()
        except:
            _api_exception_handler(RESPONSE, "Move Schedule Item Failed")