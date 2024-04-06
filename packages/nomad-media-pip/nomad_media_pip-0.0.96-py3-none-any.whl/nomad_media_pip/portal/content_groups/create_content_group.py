from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

def _create_content_group(AUTH_TOKEN, URL, CONTENT_GROUP_NAME, DEBUG):
    API_URL = f"{URL}/api/contentGroup"
    
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "Name": CONTENT_GROUP_NAME
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
   	
    except:
      	_api_exception_handler(RESPONSE, "Create content groups failed")