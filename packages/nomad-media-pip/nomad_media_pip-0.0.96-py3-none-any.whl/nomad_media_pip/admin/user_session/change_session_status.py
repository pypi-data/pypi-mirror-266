from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _change_session_status(AUTH_TOKEN, URL, USER_ID, USER_SESSION_STATUS, 
                          APPLICATION_ID, DEBUG):

    API_URL = f"{URL}/api/admin/user-session"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "id": USER_ID,
        "userSessionStatus": USER_SESSION_STATUS,
        "applicationId": APPLICATION_ID
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
    except:
        _api_exception_handler(RESPONSE, "Change Session Status Failed")