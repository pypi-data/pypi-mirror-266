from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_live_operators(AUTH_TOKEN, URL, DEBUG):
    API_URL = f"{URL}/api/admin/liveOperator"

    HEADERS = {
        "Authorization": "Bearer " +  AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers= HEADERS)

        # If not found return None
        if (not RESPONSE.ok):
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Getting Live Operators failed")