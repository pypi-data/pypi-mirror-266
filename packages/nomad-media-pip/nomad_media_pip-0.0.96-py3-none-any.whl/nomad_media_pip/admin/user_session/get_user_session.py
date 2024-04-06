from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_user_session(AUTH_TOKEN, URL, API_TYPE, USER_ID, DEBUG):

    API_URL = f"{URL}/api/admin/user-session/{USER_ID}" if API_TYPE == "admin" else f"{URL}/api/user-session/{USER_ID}"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Get User Session Failed")
