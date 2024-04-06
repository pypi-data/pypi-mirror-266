from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

def _verify(URL, EMAIL, CODE, DEBUG):
    API_URL = f"{URL}/api/account/verify"

    HEADERS = {
        "Content-Type": "application/json"
    }
    
    # replace username and password with your username and password
    BODY = {
    	"userName": EMAIL, 
        "token": CODE
    }

    if DEBUG:
        print(f"API_URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Verification failed")
            
