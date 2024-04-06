from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _stop_sharing_content_group_with_user(AUTH_TOKEN, URL, CONTENT_GROUP_ID, USER_IDS, DEBUG):
  
    API_URL = f"{URL}/api/contentGroup/stopshare/{CONTENT_GROUP_ID}"
    
    HEADERS = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + AUTH_TOKEN
    }
    
    BODY = USER_IDS

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
    		
        return RESPONSE.json()
      
    except:
        _api_exception_handler(RESPONSE, "Share collection to user failed: ")