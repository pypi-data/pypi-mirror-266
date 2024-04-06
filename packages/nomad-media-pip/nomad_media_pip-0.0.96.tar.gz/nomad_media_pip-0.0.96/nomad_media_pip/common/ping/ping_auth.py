from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _ping_auth(AUTH_TOKEN, URL, APPLICATION_ID, USER_SESSION_ID, DEBUG):

    API_URL = f"{URL}/api/account/ping/auth"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

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
      	_api_exception_handler(RESPONSE, "Ping Auth Failed")