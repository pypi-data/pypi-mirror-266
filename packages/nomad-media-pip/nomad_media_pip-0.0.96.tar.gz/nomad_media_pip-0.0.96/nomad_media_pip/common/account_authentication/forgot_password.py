from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _forgot_password(URL, USENAME, DEBUG):
    API_URL = f"{URL}/api/account/forgot-password"
  
    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json"
    }

    # Build the payload body
    BODY = {
        "username": USENAME
    }
    
    if DEBUG: 
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
          
    except:
        _api_exception_handler(RESPONSE, "Forgot Password Failed")