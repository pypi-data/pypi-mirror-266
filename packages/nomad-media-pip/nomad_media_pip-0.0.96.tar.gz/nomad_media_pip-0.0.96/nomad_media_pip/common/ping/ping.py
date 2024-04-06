from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

# @param {string} AUTH_TOKEN - The authentication token

def _ping(AUTH_TOKEN, URL, APPLICATION_ID, USER_SESSION_ID, DEBUG):
        
    API_URL = f"{URL}/api/account/ping"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }
    
    # replace username and password with your username and password
    BODY = {
        "userSessionId": USER_SESSION_ID
    }

    if (APPLICATION_ID):
        BODY["applicationId"] = APPLICATION_ID

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    
    except:
      	_api_exception_handler(RESPONSE, "Ping Failed")

