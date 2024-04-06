from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _change_password(AUTH_TOKEN, URL, CURRENT_PASSWORD, NEW_PASSWORD, DEBUG):
  
    API_URL = f"{URL}/api/account/change-password"
  
    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    # Build the payload body
    BODY = {
        "password": CURRENT_PASSWORD,
        "newPassword": NEW_PASSWORD
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()

    except:
        _api_exception_handler(RESPONSE, "Change password failed")