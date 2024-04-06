from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _logout(AUTH_TOKEN, URL, USER_SESSION_ID, DEBUG):
    API_URL = f"{URL}/api/account/logout"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "userSessionId": USER_SESSION_ID,   
    }

    if DEBUG:
        print(f"API URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data = json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return True

    except:
        _api_exception_handler(RESPONSE, "Logout failed")

