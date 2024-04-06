from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _change_email(AUTH_TOKEN, URL, EMAIL, PASSWORD, DEBUG):
  
    API_URL = f"{URL}/api/account/change-email"
  
    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    # Build the payload body
    BODY = {
        "password": PASSWORD,
        "newEmail": EMAIL
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Change email failed")