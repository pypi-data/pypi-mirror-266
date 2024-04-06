from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_live_output_types(AUTH_TOKEN, URL, DEBUG):
    API_URL = f"{URL}/api/lookup/117"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    # Make the request
    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()["items"]
    
    except:
        _api_exception_handler(RESPONSE, "Get Output Types Failed")
        