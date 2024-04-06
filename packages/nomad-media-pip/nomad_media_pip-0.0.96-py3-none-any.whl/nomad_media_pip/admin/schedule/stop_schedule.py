from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _stop_schedule(AUTH_TOKEN, URL, ID, FORCE_STOP, DEBUG):

    API_URL = f"{URL}/api/admin/schedule/{ID}/stop{f"?force={FORCE_STOP}" if FORCE_STOP else ""}"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Stop Schedule Failed")