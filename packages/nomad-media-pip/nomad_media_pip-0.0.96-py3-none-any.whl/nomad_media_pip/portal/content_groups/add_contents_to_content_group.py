from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

def _add_contents_to_content_group(AUTH_TOKEN, URL, CONTENT_GROUP_ID, CONTENTS, DEBUG):
    
    API_URL = f"{URL}/api/contentGroup/add/{CONTENT_GROUP_ID}"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }
    
    BODY = CONTENTS

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
   	
    except:
      	_api_exception_handler(RESPONSE, "Add content to content group failed")