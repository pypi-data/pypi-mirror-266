from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_saved_searches(AUTH_TOKEN, URL, DEBUG):

    API_URL = f"{URL}/api/portal/savedsearch"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Get saved searches failed")