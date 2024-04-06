from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _reset_password(URL, USENAME, CODE, NEW_PASSWORD, DEBUG):
    API_URL = f"{URL}/api/account/reset-password"
  
    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json"
    }

    # Build the payload body
    BODY = {
        "userName": USENAME,
        "token": CODE,
        "newPassword": NEW_PASSWORD
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
    except:
        raise Exception("Reset Password failed")